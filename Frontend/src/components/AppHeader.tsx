import type { MeResponse } from "../api/types";
import { HeaderBranding } from "./HeaderBranding";
import { HeaderAccount } from "./HeaderAccount";

type Props = {
    title: string;
    subtitle: string;
    logo: string;
    me?: MeResponse | null;
    loading: boolean;
    onReplenishBalance: () => void;
};

export function AppHeader({title, subtitle, logo, me, loading, onReplenishBalance}: Props) {
    return (
        <header className="app-header">
            <HeaderBranding title={title} subtitle={subtitle} logo={logo}/>
            <HeaderAccount me={me} loading={loading} onReplenishBalance={onReplenishBalance}/>
        </header>
    );
}
