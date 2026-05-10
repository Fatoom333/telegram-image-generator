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
                <select
                    className="tariff-selector"
                    onChange={(event) => onTariffSelect(event.target.value)}
                    value={selectedTariffId}
                > {tariffs.length === 0 ? (
                  <option value="">Тарифы не загружены</option>
                ) : (
                  tariffs.map((tariff) => (
                    <option key={tariff.id} value={tariff.id}>
						{tariff.title} · {tariff.amount_rub} ₽
                    </option>
                  	))
                )}
              </select>
            </label>
        </div>
    );
}