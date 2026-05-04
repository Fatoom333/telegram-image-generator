import type { Generation } from "../api/types";
import { StatusIndicator } from "./StatusIndicator";
import closeBtnIcon from "../assets/close_btn_icon.svg";
import downloadBtnIcon from "../assets/download_btn_icon.svg";

type Props = {
    generation: Generation;
    onClose: () => void;
};

export function GenerationCard({generation, onClose}: Props) {
    return (
        <div className="generation-card card">
            <button className="generation-card-close-btn btn" onClick={onClose} aria-label="Close">
                <img className="close-icon" src={closeBtnIcon} alt="Close icon"/>
            </button>
            <div className="generation-card-result">
                <StatusIndicator status={generation.status}/>
                <p className="generation-card-prompt">{generation.prompt}</p>
                {generation.resultUrl ? (
                    <img className="generation-card-result-image" src={generation.resultUrl} alt="Generation result"/>
                ) : ( <p>Генерация недоступна</p> )}
                <p className="generation-card-date">Дата: {new Date(generation.createdAt).toLocaleString("ru-RU")}</p>
                <a 
                    className="generation-card-download-btn btn" 
                    href={generation.resultUrl ?? ""} 
                    download={!!generation.resultUrl} 
                    aria-label="Download">
                    <img className="download-icon" src={downloadBtnIcon} alt="Download icon"/>
                </a>
            </div>
        </div>
    );
}
