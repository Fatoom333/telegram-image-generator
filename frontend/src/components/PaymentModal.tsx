import type { TariffResponse } from "../api/types"
// import DownloadBtnIcon from "../assets/download_btn_icon.svg?react"
import { TariffSelector } from "./header/TariffSelector";
import CoinIcon from "../assets/coin_btn_icon.svg?react"

type Props = {
    tariffs: TariffResponse[];
    selectedTariffId: string;
    onTariffSelect: (id: string) => void;
    isPaying: boolean;
    onPay: () => void;
    onClose: () => void;
    error: string | null;
}

export function PaymentModal({
    tariffs, 
    selectedTariffId,
    onTariffSelect,
    isPaying,
    onPay,
    error
}: Props) {
    return (
        <div className="payment-fullscreen">
            <div className="payment-fullscreen-card card">
                <div className="payment-fullscreen-content">
                    <h2>Пополнение баланса</h2>
                    <TariffSelector
                        tariffs={tariffs}
                        selectedTariffId={selectedTariffId}
                        onTariffSelect={onTariffSelect}
                    />
                    {error && <div className="alert error-alert">{error}</div>}
                    <button
                        className="pay-btn btn payment-modal-pay"
                        disabled={isPaying}
                        onClick={onPay}
                        type="button"
                    >
                        <CoinIcon/>
                        {isPaying ? "Оплачиваем..." : "Оплатить"}
                    </button>
                </div>
            </div>
        </div>
    );
}