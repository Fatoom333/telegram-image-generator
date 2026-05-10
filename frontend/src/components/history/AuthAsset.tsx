import { useState, useEffect } from "react";
import { absoluteApiUrl } from "../../api/api";

type Props = {
    src: string;
    alt: string;
    asset_type: "image" | "video";
    onLoad?: (objectUrl: string) => void;
}

export function AuthAsset({src, alt, asset_type, onLoad}: Props) {
    const [displayUrl, setDisplayUrl] = useState<string | null>(null);
    const [error, setError] = useState(false);

    useEffect(() => {
        let cancelled = false;
        let objectUrl: string | null = null;

        async function load() {
            setError(false);
            try {
                const headers = new Headers();
                const initData = window.Telegram?.WebApp?.initData ?? "";
                if (initData) headers.set("X-Telegram-Init-Data", initData);

                const res = await fetch(absoluteApiUrl(src), { headers });
                if (!res.ok) throw new Error();
                const blob = await res.blob();
                objectUrl = URL.createObjectURL(blob);
                if (asset_type === "image") {
                    if (!cancelled) setDisplayUrl(objectUrl);
                } else {
                    const video = document.createElement("video");
                    video.preload = "metadata";
                    video.muted = true;
                    video.src = objectUrl;
                    await new Promise<void> ((resolve, reject) => {
                        video.onloadeddata = () => {
                            video.currentTime = 0;
                        };
                        video.onseeked = () => {
                            const canvas = document.createElement("canvas");
                            canvas.width = video.videoWidth;
                            canvas.height = video.videoHeight;
                            const context = canvas.getContext("2d");
                            if (context) {
                                context.drawImage(video, 0, 0, canvas.width, canvas.height);
                                const thumb = canvas.toDataURL("image/jpeg", 0.8);
                                if (!cancelled) setDisplayUrl(thumb);
                                resolve();
                            } else { reject(); }
                        };
                        video.onerror = () => reject();
                    });
                    video.remove();
                }
                onLoad?.(objectUrl);
            } catch {
                if (!cancelled) setError(true);
            }
        }

        load();
        return () => {
            cancelled = true;
            if (objectUrl) URL.revokeObjectURL(objectUrl);
        };
    }, [src, asset_type]);

    if (error) return <div className="image-placeholder">Не удалось загрузить</div>;
    if (!displayUrl) return <div className="image-placeholder">Загрузка...</div>;
    return <img src={displayUrl} alt={alt} />;
}