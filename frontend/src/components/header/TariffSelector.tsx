import type { TariffResponse } from "../../api/types";

type Props = {
    tariffs: TariffResponse[];
    selectedTariffId: string;
    onTariffSelect: (tariffId: string) => void;
};

export function TariffSelector({tariffs, selectedTariffId, onTariffSelect}: Props) {
    return (
        <div className="tariff">
            <label>
                <span>Тариф</span>
            </label>
            <div className="tariff-grid">
                {tariffs.length === 0 ? (
                    <p className="muted-text">Тарифы не загружены</p>
                ) : (
                    tariffs.map((tariff) => (
                        <button
                            key={tariff.id}
                            type="button"
                            className={`tariff-card ${selectedTariffId === tariff.id ? "tariff-card-selected" : ""}`}
                            onClick={() => onTariffSelect(tariff.id)}
                        >
                            <span className="tariff-card-title">{tariff.title}</span>
                            <span className="tariff-card-price">{tariff.amount_rub} ₽</span>
                            <span className="tariff-card-credits">{tariff.credits} кр.</span>
                        </button>
                    ))
                )}
            </div>
        </div>
    );
}