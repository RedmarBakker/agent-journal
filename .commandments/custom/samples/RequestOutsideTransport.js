export async function state() {
    // @sin RequestOutsideTransportDetector
    const answer = await fetch("./state");
    return answer.json();
}

export function stream(url) {
    // @sin RequestOutsideTransportDetector
    return new EventSource(url);
}

export async function asked(api) {
    // @righteous RequestOutsideTransportDetector
    return api.summary();
}

export function refreshers(list) {
    // @righteous RequestOutsideTransportDetector
    return list.map(([wanted, refresh]) => wanted() && refresh());
}
