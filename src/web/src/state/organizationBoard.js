import {kept, remembered} from "../platform/storage.js";
import {reactive} from "vue";

const DISPLAY_KEY = "journal.organization.board";
const display = remembered(DISPLAY_KEY, {hideDone: false});

// The board's shared text filter and the completed-plan preference, used on a domain page and Home.
export const organizationBoard = reactive({words: "", hideDone: Boolean(display.hideDone)});

kept(DISPLAY_KEY, () => ({hideDone: organizationBoard.hideDone}));
