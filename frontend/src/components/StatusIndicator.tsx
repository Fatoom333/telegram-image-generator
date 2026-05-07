import type { GenerationStatus } from "../api/types";

const statusTexts: Record<GenerationStatus, string> = {
    query: "Ожидаем",
    successful: "Готово",
    failed: "Ошибка"
};

type Props = {
    status: GenerationStatus;
};

export function StatusIndicator({status}: Props) {
    return (
        <span className={`generation-status status-${status}`}>{statusTexts[status]}</span>
    );
}