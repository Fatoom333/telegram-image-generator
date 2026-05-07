import { HistoryList } from "./HistoryList";
import { GenerationCard } from "./GenerationCard";
import type { GenerationResponse } from "../api/types";
import { useState } from "react";

type Props = {
    generations: GenerationResponse[];
};

export function HistoryModule({ generations }: Props) {
    const [selected, setSelected] = useState<GenerationResponse | null>(null);
    return (
        <>
            <HistoryList
                generations={generations} 
                onSelect={setSelected}
            />
            {selected && (
                <div className="modal-overlay" onClick={() => setSelected(null)}>
                    <div className="modal-content" onClick={e => e.stopPropagation()}>
                        <GenerationCard generation={selected} onClose={() => setSelected(null)}/>
                    </div>
                </div>
            )}
        </>
    );
}