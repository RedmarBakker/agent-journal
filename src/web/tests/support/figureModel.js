import {readFileSync} from "node:fs";
import {createRequire} from "node:module";
import {fileURLToPath} from "node:url";

const directory = new URL("../../public/voices/figures/", import.meta.url);
const files = JSON.parse(readFileSync(new URL("figures.json", directory)));
const decoderDirectory = new URL("draco/", directory);
const require = createRequire(import.meta.url);
const decoderSource = readFileSync(new URL("draco_wasm_wrapper.js", decoderDirectory), "utf8");
const factory = new Function("require", "module", "exports", "__dirname", `${decoderSource}\nreturn DracoDecoderModule;`)(require, {exports: {}}, {}, fileURLToPath(decoderDirectory));
const decoder = factory({wasmBinary: readFileSync(new URL("draco_decoder.wasm", decoderDirectory))});
const cache = new Map();
const dimensions = {SCALAR: 1, VEC2: 2, VEC3: 3, VEC4: 4, MAT4: 16};
const components = {5120: Int8Array, 5121: Uint8Array, 5122: Int16Array, 5123: Uint16Array, 5125: Uint32Array, 5126: Float32Array};

// The shipped decoder expands the shipped models, retaining their nodes, skins and accessor metadata.
export async function decodedFigure(voice) {
    if (cache.has(voice)) {
        const model = await cache.get(voice);
        return {...model, buffer: model.buffer.slice(0)};
    }
    const pending = (async () => {
        const source = readFileSync(new URL(files[voice], directory));
        const jsonLength = source.readUInt32LE(12);
        const json = JSON.parse(source.subarray(20, 20 + jsonLength).toString());
        const binaryLength = source.readUInt32LE(20 + jsonLength);
        const binary = source.subarray(28 + jsonLength, 28 + jsonLength + binaryLength);
        const chunks = [binary, Buffer.alloc((4 - binary.length % 4) % 4)];
        let offset = chunks.reduce((sum, chunk) => sum + chunk.length, 0);
        const draco = await decoder;
        const decode = new draco.Decoder();
        const append = (array, original) => {
            const bytes = Buffer.from(array.buffer, array.byteOffset, array.byteLength);
            const view = json.bufferViews.push({buffer: 0, byteOffset: offset, byteLength: bytes.length}) - 1;
            const accessor = json.accessors.push({...original, bufferView: view, byteOffset: 0}) - 1;
            const padding = Buffer.alloc((4 - bytes.length % 4) % 4);
            chunks.push(bytes, padding);
            offset += bytes.length + padding.length;
            return accessor;
        };
        for (const mesh of json.meshes) for (const primitive of mesh.primitives) {
            const compression = primitive.extensions?.KHR_draco_mesh_compression;
            if (!compression) continue;
            const view = json.bufferViews[compression.bufferView];
            const data = binary.subarray(view.byteOffset ?? 0, (view.byteOffset ?? 0) + view.byteLength);
            const buffer = new draco.DecoderBuffer();
            buffer.Init(data, data.byteLength);
            const geometry = new draco.Mesh();
            const status = decode.DecodeBufferToMesh(buffer, geometry);
            if (!status.ok()) throw new Error(`Cannot decode ${voice}/${mesh.name}: ${status.error_msg()}`);
            for (const [name, uniqueId] of Object.entries(compression.attributes)) {
                const original = json.accessors[primitive.attributes[name]];
                const attribute = decode.GetAttributeByUniqueId(geometry, uniqueId);
                const values = new draco.DracoFloat32Array();
                decode.GetAttributeFloatForAllPoints(geometry, attribute, values);
                const array = new components[original.componentType](original.count * dimensions[original.type]);
                for (let index = 0; index < array.length; index++) array[index] = values.GetValue(index);
                primitive.attributes[name] = append(array, original);
                draco.destroy(values);
            }
            const original = json.accessors[primitive.indices];
            const faces = new components[original.componentType](geometry.num_faces() * 3);
            const face = new draco.DracoInt32Array();
            for (let index = 0; index < geometry.num_faces(); index++) {
                decode.GetFaceFromMesh(geometry, index, face);
                for (let corner = 0; corner < 3; corner++) faces[index * 3 + corner] = face.GetValue(corner);
            }
            primitive.indices = append(faces, original);
            delete primitive.extensions.KHR_draco_mesh_compression;
            if (!Object.keys(primitive.extensions).length) delete primitive.extensions;
            draco.destroy(face);
            draco.destroy(geometry);
            draco.destroy(buffer);
        }
        draco.destroy(decode);
        for (const key of ["extensionsUsed", "extensionsRequired"]) {
            json[key] = json[key]?.filter((name) => name !== "KHR_draco_mesh_compression");
            if (!json[key]?.length) delete json[key];
        }
        json.buffers[0].byteLength = offset;
        const data = Buffer.concat(chunks);
        const jsonBytes = Buffer.from(JSON.stringify(json));
        const paddedJson = Buffer.concat([jsonBytes, Buffer.alloc((4 - jsonBytes.length % 4) % 4, 0x20)]);
        const glb = Buffer.alloc(28 + paddedJson.length + data.length);
        glb.writeUInt32LE(0x46546c67, 0);
        glb.writeUInt32LE(2, 4);
        glb.writeUInt32LE(glb.length, 8);
        glb.writeUInt32LE(paddedJson.length, 12);
        glb.writeUInt32LE(0x4e4f534a, 16);
        paddedJson.copy(glb, 20);
        glb.writeUInt32LE(data.length, 20 + paddedJson.length);
        glb.writeUInt32LE(0x004e4942, 24 + paddedJson.length);
        data.copy(glb, 28 + paddedJson.length);
        return {json, binary: data, buffer: glb.buffer.slice(glb.byteOffset, glb.byteOffset + glb.byteLength)};
    })();
    cache.set(voice, pending);
    const model = await pending;
    return {...model, buffer: model.buffer.slice(0)};
}

export function attributeOf(model, index) {
    const accessor = model.json.accessors[index];
    const view = model.json.bufferViews[accessor.bufferView];
    const ArrayType = components[accessor.componentType];
    const start = (view.byteOffset ?? 0) + (accessor.byteOffset ?? 0);
    const bytes = model.binary.subarray(start, start + accessor.count * dimensions[accessor.type] * ArrayType.BYTES_PER_ELEMENT);
    const copy = Uint8Array.from(bytes);
    return new ArrayType(copy.buffer);
}
