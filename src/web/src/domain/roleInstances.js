import {workerName} from "./workers.js";
import {updatedAt} from "./row.js";
import {clock} from "../format/time.js";

export const isRoleWorker = (worker, role) => worker.role === role || (!worker.role && worker.profile === role);

export function roleWorkOf(agent, role) {
    const stack = agent.stack || [];
    if (!stack.some((layer) => layer.state === "role_work" && layer.data?.role === role)) return null;
    const plan = [...stack].reverse().find((layer) => ["following_plan", "leading_plan"].includes(layer.state))?.data?.plan_id || 0;
    const task = [...stack].reverse().find((layer) => layer.state === "following_plan")?.data?.task_id || 0;
    return {plan_id: plan, task_id: task};
}

export function roleInstances(role, {workers = [], agents = [], plans = []}) {
    const plansById = new Map(plans.map((plan) => [`${plan.environment}:${plan.id}`, plan]));
    const agentsById = new Map(agents.map((agent) => [`${agent.environment}:${agent.id}`, agent]));
    const workerRows = workers.filter((worker) => isRoleWorker(worker, role.id));
    const found = workerRows.map((worker) => {
        const legacy = !worker.role && worker.profile === role.id;
        const plan = plansById.get(`${worker.environment}:${worker.plan_id}`) || null;
        return {
            key: `worker:${worker.environment}:${worker.id}`,
            kind: plan?.mode === "organization" ? "seat" : "worker",
            env: worker.environment,
            name: workerName(worker),
            legacy,
            worker,
            agent: agentsById.get(`${worker.environment}:${worker.agent}`) || null,
            plan,
            plan_id: worker.plan_id || 0,
            task_id: worker.task?.task_id || 0,
        };
    });

    for (const agent of agents) {
        const work = roleWorkOf(agent, role.id);
        if (!work) continue;
        const plan = plansById.get(`${agent.environment}:${work.plan_id}`) || null;
        found.push({
            key: `agent:${agent.environment}:${agent.id}`,
            kind: "solo",
            env: agent.environment,
            name: role.title,
            legacy: false,
            worker: null,
            agent,
            plan,
            plan_id: work.plan_id,
            task_id: work.task_id,
        });
    }

    return found.sort((one, other) => (updatedAt(other.worker || other.agent) || 0) - (updatedAt(one.worker || one.agent) || 0));
}

export const roleInstanceTitle = (instance) => {
    const row = instance.worker || instance.agent;
    return [
        instance.name,
        instance.plan_id && (instance.plan?.title ? `Plan ${instance.plan_id}: ${instance.plan.title}` : `Plan ${instance.plan_id}`),
        instance.task_id && `Task ${instance.task_id}`,
        row?.created_at && `Started ${clock(row.created_at)}`,
    ].filter(Boolean).join(" · ");
};
