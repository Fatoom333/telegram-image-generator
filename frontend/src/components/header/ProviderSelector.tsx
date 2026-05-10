import type { PaymentProviderResponse } from "../../api/types";

type Props = {
    providers: PaymentProviderResponse[];
    selectedProvider: string;
    onProviderSelect: (providerId: string) => void;
};

export function ProviderSelector({providers, selectedProvider, onProviderSelect}: Props) {
    return (
        <div className="provider">
            <label>
            <span>Способ оплаты</span>
            <select
                className="provider-selector"
                onChange={(event) => onProviderSelect(event.target.value)}
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