export const PAGE = 50;
export const RECENT = 100;

// how many rows one page of a table holds: the chat opens with its latest 25 messages, every other table with 50
const TABLE_PAGES = {messages: 25};
export const pageOf = (table) => TABLE_PAGES[table] || PAGE;
