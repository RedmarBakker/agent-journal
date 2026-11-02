import {createApp, h} from "vue";
import {afterEach, expect, test, vi} from "vitest";

const api = {supervisorProposalCount: vi.fn()};
vi.mock("../src/api/client.js", async (importOriginal) => ({...(await importOriginal()), api}));

const {useNavigation} = await import("../src/composables/navigation.js");

let app = null;
let host = null;

afterEach(() => {
    app?.unmount();
    app = null;
    host?.remove();
    host = null;
    document.body.innerHTML = "";
});

function openNavigation() {
    let sections;
    const Root = {
        setup() {
            sections = useNavigation().sections;
            return () => h("span", sections.value.find((section) => section.key === "environment")
                .links.find((link) => link.key === "supervisor").count);
        },
    };
    host = document.body.appendChild(document.createElement("div"));
    app = createApp(Root);
    app.mount(host);
    return host;
}

test("the Supervisor sidebar link shows how many proposals wait for the owner", async () => {
    api.supervisorProposalCount.mockReset().mockResolvedValue({count: 4});
    const page = openNavigation();

    await vi.waitFor(() => expect(page.textContent).toBe("4"));
    expect(api.supervisorProposalCount).toHaveBeenCalledOnce();
});
