import { useState } from "react";
import { GenerationCard } from "./GenerationCard";
import type { GenerationResponse } from "../../api/types";
import CloseBtnIcon from "../../assets/close_btn_icon.svg?react";
import { CardHeader } from "../misc/CardHeader";
import HistoryIcon from "../../assets/history_icon.svg?react";

type Props = {
    generations: GenerationResponse[];
    isBootLoading?: boolean;
};

export function HistoryList({ generations, isBootLoading = false }: Props) {
    const [viewImageUrl, setViewImageUrl] = useState<string | null>(null);
    const [viewVideoUrl, setViewVideoUrl] = useState<string | null>(null);
    if (isBootLoading) {
        return (
            <div className="empty-state">
                <div className="folder-icon">✦</div>
                <h2>Загружаем историю...</h2>
                <p>Пожалуйста, подождите</p>
            </div>
        );
    }
    if (generations.length === 0) {
        return (
            <div className="empty-state">
                <h2>Пока нет генераций</h2>
                <p>Самое время это исправить!</p>
            </div>
        );
    }
    return (
        <>
            <div className="history-list">
                <CardHeader
                    icon={<HistoryIcon/>}
                    title="История"
                />
                {Array.isArray(generations) && generations.map((gen) => (
                    <GenerationCard
                        key={gen.id}
                        generation={gen}
                        onImageClick={(url) => setViewImageUrl(url)}
                        onVideoClick={(url) => setViewVideoUrl(url)}
                    />
                ))}
            </div>
            {viewImageUrl && (
                <div
                    className="image-modal-overlay"
                    onClick={() => setViewImageUrl(null)}
                >
                    <div
                        className="image-modal-card"
                        onClick={(e) => e.stopPropagation()}
                    >
                        <img
                            src={viewImageUrl}
                            alt="Просмотр изображения"
                            className="image-modal-img"
                        />
                        <button
                            className="image-modal-close"
                            onClick={() => setViewImageUrl(null)}
                        >
                            <CloseBtnIcon/>
                        </button>
                    </div>
                </div>
            )}
            {viewVideoUrl && (
                <div
                    className="image-modal-overlay"
                    onClick={() => setViewVideoUrl(null)}
                >
                    <div
                        className="image-modal-card"
                        onClick={(e) => e.stopPropagation()}
                    >
                        <video
                            src={viewVideoUrl}
                            controls
                            className="image-modal-img"
                            style={{ maxWidth: "100%", maxHeight: "85vh" }}
                        />
                        <button
                            className="image-modal-close"
                            onClick={() => setViewVideoUrl(null)}
                        >
                            <CloseBtnIcon/>
                        </button>
                    </div>
                </div>
            )}
        </>
    );
}