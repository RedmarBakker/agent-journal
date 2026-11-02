import {PAGES, pluralTitle} from "../domain/navigation.js";
import {meta} from "../domain/tables.js";
import {computed} from "vue";
import {route} from "../route.js";

const TITLES = {search: "Search", about: "About", file: "File"};

export const pageTitle = computed(() => {
    if (!route.value.page) return "Home";
    const page = PAGES[route.value.page];
    const subpage = page?.children?.find(({key}) => key === route.value.sub)
        || (!route.value.sub ? page?.children?.[0] : null);
    if (subpage) return `${page.title} › ${subpage.title}`;
    return page?.title || TITLES[route.value.page] || (meta(route.value.page) ? pluralTitle(meta(route.value.page).title) : route.value.page);
});
