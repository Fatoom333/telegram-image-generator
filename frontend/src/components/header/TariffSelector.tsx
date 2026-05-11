import type { TariffResponse } from "../../api/types";

type Props = {
    tariffs: TariffResponse[];
    selectedTariffId: string;
    onTariffSelect: (tariffId: string) => void;
};

export function TariffSelector({tariffs, selectedTariffId, onTariffSelect}: Props) {
    const isOdd = tariffs.length % 2 !== 0;
    return (
        <div className="tariff">
            <label>
                <span>Тариф</span>
            </label>
            <div className="tariff-grid">
                {tariffs.length === 0 ? (
                    <p className="muted-text">Тарифы не загружены</p>
                ) : (
                    tariffs.map((tariff, index) => {
                        const isSelected = selectedTariffId === tariff.id;
                        const isLastOdd = isOdd && index === tariffs.length - 1;
                        return (
                            <button
                                key={tariff.id}
                                type="button"
                                className={`tariff-card 
                                    ${isSelected ? "tariff-card-selected" : ""}
                                    ${isLastOdd ? "tariff-card-span-2" : ""}`}
                                onClick={() => onTariffSelect(tariff.id)}
                            >
                                <span className="tariff-card-title">{tariff.title}</span>
                                <span className="tariff-card-price">{tariff.amount_rub} ₽</span>
                                <span className="tariff-card-credits">{tariff.credits} кредитов</span>
                            </button>
                        );
                    })
                )}
            </div>
        </div>
    );
}