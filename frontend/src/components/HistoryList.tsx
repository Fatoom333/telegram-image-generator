import { useMemo } from "react";
import type { Generation } from "../api/types";
import { EmptyStateIndicator } from "./EmptyStateIndicator";
import { StatusIndicator } from "./StatusIndicator";

type Props = {
    generations: Generation[];
    onSelect: (generation: Generation) => void;
}

export function HistoryList({generations, onSelect}: Props) {
    const sortedGenerations = useMemo(() => {
        return [...generations].sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());
    }, [generations]);  
    return (
        <div className="history-list-card card">
            <h2><span className="bold-text">История</span></h2>
            {generations.length === 0 ? (
                <EmptyStateIndicator
                    title="Пока нет генераций"
                    description="Самое время это исправить!"
                />
            ) : (
                <ul className="history-list">
                    {sortedGenerations.map((generation) => (
                        <li key={generation.id} onClick={() => onSelect(generation)}>
                            <StatusIndicator status={generation.status}/>
                            <p>{generation.prompt}</p>
                            <p>{new Date(generation.createdAt).toLocaleString("ru-RU")}</p>
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
}