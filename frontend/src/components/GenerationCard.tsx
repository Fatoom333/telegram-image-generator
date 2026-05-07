import type { GenerationResponse } from "../api/types";
import { StatusIndicator } from "./StatusIndicator";
import CloseBtnIcon from "../assets/close_btn_icon.svg?react";
import DownloadBtnIcon from "../assets/download_btn_icon.svg?react";

type Props = {
    generation: GenerationResponse;
    onClose: () => void;
};

export function GenerationCard({generation, onClose}: Props) {
    const resultUrl = generation.images?.find((item) => item.role === "generated" && item.file_url)?.file_url ?? generation.images?.[0]?.file_url ?? null;

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
                {resultUrl ? (
                    <img className="generation-card-result-image" src={resultUrl} alt="Generation result"/>
                ) : ( <p>Генерация недоступна</p> )}

                <div className="generation-card-result-date-download">
                    <p className="generation-card-date">Дата: {new Date(generation.craeted_at).toLocaleString("ru-RU")}</p>
                    <a 
                        className="generation-card-download-btn btn" 
                        href={resultUrl ?? ""} 
                        download={!!resultUrl} 
                        aria-label="Download">
                        <DownloadBtnIcon/>
                    </a>
                </div>
            </div>
        </div>
    );
}
