import type { Generation } from "../api/types";
import { StatusIndicator } from "./StatusIndicator";
import CloseBtnIcon from "../assets/close_btn_icon.svg?react";
import DownloadBtnIcon from "../assets/download_btn_icon.svg?react";

type Props = {
    generation: Generation;
    onClose: () => void;
};

export function GenerationCard({generation, onClose}: Props) {
    return (
        <div className="generation-card card">
            <div className="generation-card-top">
                <div className="generation-card-main-info">
                    <StatusIndicator status={generation.status}/>

                    <p className="generation-card-prompt">{generation.prompt}</p>
                </div>
                
                <button className="generation-card-close-btn btn" onClick={onClose} aria-label="Close">
                <CloseBtnIcon/>
                </button>
            </div>
            
            <div className="generation-card-result">
                {generation.resultUrl ? (
                    <img className="generation-card-result-image" src={generation.resultUrl} alt="Generation result"/>
                ) : ( <p>Генерация недоступна</p> )}

                <div className="generation-card-result-date-download">
                    <p className="generation-card-date">Дата: {new Date(generation.createdAt).toLocaleString("ru-RU")}</p>
                    <a 
                        className="generation-card-download-btn btn" 
                        href={generation.resultUrl ?? ""} 
                        download={!!generation.resultUrl} 
                        aria-label="Download">
                        <DownloadBtnIcon/>
                    </a>
                </div>
            </div>
        </div>
    );
}
