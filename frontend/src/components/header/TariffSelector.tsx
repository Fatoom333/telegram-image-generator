import type { TariffResponse } from "../../api/types";

type Props = {
    tariffs: TariffResponse[];
    selectedTariffId: string;
    onSelect: (tariffId: string) => void;
};

export function TariffSelector({tariffs, selectedTariffId, onSelect}: Props) {
    return (
        <div className="tariff">
            <label>
                Тариф
                <select
                    className="tariff-selector"
                    onChange={(event) => onSelect(event.target.value)}
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