import { useState, useEffect } from "react";
import { absoluteApiUrl } from "../../api/api";

export function AuthImage({ src, alt, onLoad }: { src: string; alt: string; onLoad?: (objectUrl: string) => void }) {
    const [objectUrl, setObjectUrl] = useState<string | null>(null);
    const [isFailed, setIsFailed] = useState(false);

    useEffect(() => {
        let cancelled = false;
        let createdUrl: string | null = null;

        async function load() {
            setIsFailed(false);
            try {
                const headers = new Headers();
                const initData = window.Telegram?.WebApp?.initData ?? "";
                if (initData) headers.set("X-Telegram-Init-Data", initData);

                const res = await fetch(absoluteApiUrl(src), { headers });
                if (!res.ok) throw new Error();
                const blob = await res.blob();
                createdUrl = URL.createObjectURL(blob);
                if (!cancelled) {
                    setObjectUrl(createdUrl);
                    onLoad?.(createdUrl);
                }
            } catch {
                if (!cancelled) setIsFailed(true);
            }
        }

        load();
        return () => {
            cancelled = true;
            if (createdUrl) URL.revokeObjectURL(createdUrl);
        };
    }, [src]);

    if (isFailed) return <div className="image-placeholder">Не удалось загрузить</div>;
    if (!objectUrl) return <div className="image-placeholder">Загрузка...</div>;
    return <img src={objectUrl} alt={alt} />;
}