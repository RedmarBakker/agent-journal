import {createApp} from "vue";
import {afterEach, expect, test, vi} from "vitest";
import {flush} from "./flush.js";

const {api} = await import("../src/api/client.js");
const {default: TeamConnectForm} = await import("../src/resource/TeamConnectForm.vue");

let app = null;

afterEach(() => {
    app?.unmount();
    document.body.innerHTML = "";
    vi.restoreAllMocks();
});

test("what the user types in the connect form is what the form posts", async () => {
    const connect = vi.spyOn(api, "connectTeam").mockImplementation(async () => ({team: "Team Jesse"}));
    const host = document.createElement("div");
    document.body.append(host);
    app = createApp(TeamConnectForm);
    app.mount(host);
    await flush();
    const inputs = [...host.querySelectorAll("input")];
    const typed = ["https://203.0.113.5:8444/setup?code=abc", "Team Jesse", "dev@example.com", "Jesse", "a long secret"];
    inputs.forEach((input, i) => {
        input.value = typed[i];
        input.dispatchEvent(new Event("input"));
    });
    host.querySelector("form").dispatchEvent(new Event("submit"));
    await flush();
    expect(connect).toHaveBeenCalledWith({url: typed[0], team: typed[1], email: typed[2], name: typed[3], password: typed[4]});
});
