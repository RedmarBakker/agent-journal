export function supervisorGrantChange(control, change) {
    return {
        protocol_version: 1,
        grant_id: control.grant_id,
        expected_grant_version: control.grant_version,
        change,
    };
}
