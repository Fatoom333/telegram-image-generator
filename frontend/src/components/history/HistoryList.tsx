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
    const [viewImage, setViewImage] = useState<string | null>(null);
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
                <div className="folder-icon">✦</div>
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
                        onImageClick={(url) => setViewImage(url)}
                    />
                ))}
            </div>
            {viewImage && (
                <div
                    className="image-modal-overlay"
                    onClick={() => setViewImage(null)}
                >
                    <div
                        className="image-modal-card"
                        onClick={(e) => e.stopPropagation()}
                    >
                        <img
                            src={viewImage}
                            alt="Просмотр изображения"
                            className="image-modal-img"
                        />
                        <button
                            className="image-modal-close"
                            onClick={() => setViewImage(null)}
                        >
                            <CloseBtnIcon/>
                        </button>
                    </div>
                </div>
            )}
        </>
    );
}