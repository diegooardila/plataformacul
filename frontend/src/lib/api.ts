export async function apiFetch<T>(
    endpoint: string,
    options: {
        method?: string;
        headers?: Record<string, string>;
        body?: any;
    } = {}
): Promise<T> {

    const { body, ...rest } = options;

    const headers: Record<string, string> = {
        'Content-Type': 'application/json',
        ...(options.headers || {})
    };

    const token = localStorage.getItem('token');
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const res = await fetch(endpoint, {
        ...rest,
        headers,
        credentials: 'include',
        body: body ? JSON.stringify(body) : undefined
    });

    if (!res.ok) {
        let detail = `Error ${res.status}`;
        try {
            const errBody = await res.json();
            if (errBody.detail) detail = errBody.detail;
        } catch {}
        throw new Error(detail);
    }

    return res.json();
}