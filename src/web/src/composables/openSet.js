import {ref} from "vue";

// the keys of the rows shown open in a list, each opened and closed again by flip
export function useOpenSet() {
    const opened = ref(new Set());
    const flip = (key) => {
        const next = new Set(opened.value);
        next.has(key) ? next.delete(key) : next.add(key);
        opened.value = next;
    };
    return {opened, flip};
}
