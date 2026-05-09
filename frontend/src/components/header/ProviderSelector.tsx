import type { PaymentProviderResponse } from "../../api/types";

type Props = {
    providers: PaymentProviderResponse[];
    selectedProvider: string;
    onSelect: (providerId: string) => void;
};

export function ProviderSelector({providers, selectedProvider, onSelect}: Props) {
    return (
        <div className="provider">
            <label>
            Способ оплаты
            <select
                className="provider-selector"
                onChange={(event) => onSelect(event.target.value)}
                value={selectedProvider}
            > {providers.length === 0 ? (
                <option value="">Способы оплаты не загружены</option>
            ) : (
                    providers.map((provider) => (<option key={provider.id} value={provider.id}>{provider.title}</option>)))}
            </select>
            </label>
        </div>
    );
}