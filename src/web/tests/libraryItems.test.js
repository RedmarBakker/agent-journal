import {expect, test, vi} from "vitest";
import {createApp, h, nextTick} from "vue";
import {api} from "../src/api/client.js";
import LibraryItemPanel from "../src/resource/LibraryItemPanel.vue";
import LibraryItemRow from "../src/resource/LibraryItemRow.vue";

const item = {item_type: "sequence", name: "release", description: "How a release goes out"};
const version = (number, note = "") => ({number, note, published_at: 1793300000 + number});

function mounted(component, props) {
    const root = document.createElement("div");
    createApp({render: () => h(component, props)}).mount(root);
    return root;
}

const settled = async () => {
    for (let n = 0; n < 4; n += 1) await nextTick();
};

test("a library row names its newest version and, once imported, the version imported here", () => {
    expect(mounted(LibraryItemRow, {item, version: version(2)}).textContent).not.toContain("Imported");
    expect(mounted(LibraryItemRow, {item, version: version(2), imported: 1}).textContent).toContain("Imported: version 1");
    expect(mounted(LibraryItemRow, {item, version: version(2), imported: 2}).textContent).toContain("Imported");
});

test("an item not imported offers its newest version, and one imported behind it offers the update", async () => {
    const read = vi.spyOn(api, "libraryItem").mockResolvedValue({item, versions: [version(1), version(2, "the tag step")], imported_version: 0, edited_fields: []});
    const imported = vi.spyOn(api, "importLibraryItem").mockResolvedValue({});
    let root = mounted(LibraryItemPanel, {type: "sequence", name: "release"});
    await settled();
    expect(root.textContent).toContain("the tag step");
    [...root.querySelectorAll("button")].find((b) => b.textContent.includes("Import version 2")).click();
    await settled();
    expect(imported).toHaveBeenLastCalledWith("sequence", "release", 2, false);
    read.mockResolvedValue({item, versions: [version(1), version(2)], imported_version: 1, edited_fields: []});
    root = mounted(LibraryItemPanel, {type: "sequence", name: "release"});
    await settled();
    expect(root.textContent).toContain("Update to version 2");
    read.mockRestore();
    imported.mockRestore();
});

test("a copy edited here is not updated by a press but offered to be replaced, naming what was edited", async () => {
    const read = vi.spyOn(api, "libraryItem").mockResolvedValue({item, versions: [version(1), version(2)], imported_version: 1, edited_fields: ["steps"]});
    const updated = vi.spyOn(api, "updateLibraryItem").mockResolvedValue({});
    const root = mounted(LibraryItemPanel, {type: "sequence", name: "release"});
    await settled();
    expect(root.textContent).not.toContain("Update to version 2");
    expect(root.textContent).toContain("edited: steps");
    [...root.querySelectorAll("button")].find((b) => b.textContent.includes("Replace the copy")).click();
    await settled();
    expect(updated).toHaveBeenLastCalledWith("sequence", "release", true);
    read.mockRestore();
    updated.mockRestore();
});

test("a sequence's panel names the library version its copy came from, and publishes it with its note", async () => {
    const LibraryStanding = (await import("../src/resource/LibraryStanding.vue")).default;
    const status = vi.spyOn(api, "library").mockResolvedValue({connected: true});
    const copies = vi.spyOn(api, "libraryCopies").mockResolvedValue({copies: [{item_type: "sequence", name: "release", version: 3, place: "sequences:7"}]});
    const publish = vi.spyOn(api, "publishLibraryItem").mockResolvedValue({number: 4});
    const root = mounted(LibraryStanding, {type: "sequence", reference: 7, place: "sequences:7"});
    await settled();
    expect(root.textContent).toContain("From the library: version 3");
    [...root.querySelectorAll("button")].find((b) => b.textContent.includes("Publish to the library")).click();
    await settled();
    [...root.querySelectorAll("button")].find((b) => b.textContent.trim() === "Publish").click();
    await settled();
    expect(publish).toHaveBeenLastCalledWith("sequence", "7", "", null);
    [status, copies, publish].forEach((spy) => spy.mockRestore());
});

test("with no library connected a panel shows nothing of the library", async () => {
    const LibraryStanding = (await import("../src/resource/LibraryStanding.vue")).default;
    const status = vi.spyOn(api, "library").mockResolvedValue({connected: false});
    const root = mounted(LibraryStanding, {type: "template", reference: 2, place: "templates:2"});
    await settled();
    expect(root.textContent.trim()).toBe("");
    status.mockRestore();
});

test("a reader not imported shows its script, and its import is the import of a script read", async () => {
    const body = JSON.stringify({file: "errors.pattern", text: "error:"});
    const read = vi.spyOn(api, "libraryItem").mockResolvedValue({item: {...item, item_type: "reader", name: "errors"}, versions: [{...version(1), body}], imported_version: 0, edited_fields: []});
    const imported = vi.spyOn(api, "importLibraryItem").mockResolvedValue({});
    const root = mounted(LibraryItemPanel, {type: "reader", name: "errors"});
    await settled();
    expect(root.querySelector("pre").textContent).toBe("error:");
    [...root.querySelectorAll("button")].find((b) => b.textContent.includes("its script read")).click();
    await settled();
    expect(imported).toHaveBeenLastCalledWith("reader", "errors", 1, true);
    read.mockRestore();
    imported.mockRestore();
});

test("a skill not imported says the folder its import writes", async () => {
    const read = vi.spyOn(api, "libraryItem").mockResolvedValue({item: {...item, item_type: "skill", name: "release-notes"}, versions: [version(1)], imported_version: 0, edited_fields: []});
    const root = mounted(LibraryItemPanel, {type: "skill", name: "release-notes"});
    await settled();
    expect(root.textContent).toContain(".claude/skills/release-notes");
    read.mockRestore();
});
