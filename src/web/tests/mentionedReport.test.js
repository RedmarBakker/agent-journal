import {beforeEach, expect, test} from "vitest";
import {render} from "../src/text/index.js";
import "../src/text/all.js";
import {store} from "../src/state/store.js";

beforeEach(() => {
    store.rows = {reports: [{table: "reports", id: 1072, title: "Plan 1032 reviewed for what is missing", body: "## What was reviewed\n\nThe plan's phases."}]};
});

test("a message that names a report shows its kind, number and title, never its opening section, and opens the row on a click", () => {
    const html = render("report 1072", {env: "dev"});
    expect(html).toContain("Report 1072");
    expect(html).toContain("Plan 1032 reviewed for what is missing");
    expect(html).toContain('data-peek="reports:1072"');
    expect(html).not.toContain("What was reviewed");
});
