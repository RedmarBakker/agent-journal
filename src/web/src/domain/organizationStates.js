// The states every screen of the agentic organization shows when it has nothing to draw, in one place: a title, what it means and what to do. A new screen picks one by key and never words its own.
export const ORGANIZATION_STATES = {
    loading: {tone: "loading", title: "Loading", text: "Reading the organization."},
    "no-folder": {tone: "empty", title: "No organization folder set", text: "Set the Agentic organization folder in Settings, under Organization, to the folder holding your domains and Roles."},
    contracts: {tone: "problem", title: "Some contracts have problems", text: "The organization folder has contract files the journal cannot read. Fix the files listed, then reload."},
    openrig: {tone: "problem", title: "OpenRig is not available", text: "The journal cannot reach OpenRig, or its version is not the one set in Settings. Start OpenRig or change the OpenRig version setting."},
    "agents-off": {tone: "empty", title: "Plan agents are off", text: "Turn on Plan agents in Settings, under Plans, to use the organization."},
    "no-plans": {tone: "empty", title: "This domain has no plans yet", text: "A plan that works in this domain will appear here."},
    "never-ran": {tone: "empty", title: "This Role has not run yet", text: "Its work will appear here after a plan first gives it a job."},
    failed: {tone: "problem", title: "Could not load", text: "The journal did not answer. Reload the page, and check that the server is running."},
};
