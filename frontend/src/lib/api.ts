export async function apiFetch<T>(
    endpoint: string,
    options: {
        method?: string;
        headers?: Record<string, string>;
        body?: any;
    } = {}
): Promise<T> {

    const { body, ...rest } = options;

    const res = await fetch(endpoint, {
        ...rest,
        headers: {
            'Content-Type': 'application/json',
            ...(options.headers || {})
        },
        body: body ? JSON.stringify(body) : undefined
    });

    if (!res.ok) {
        throw new Error(`HTTP error: ${res.status}`);
    }

    return res.json();
}