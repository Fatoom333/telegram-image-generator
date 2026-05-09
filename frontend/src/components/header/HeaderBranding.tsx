import type { ReactNode } from "react";

type Props = {
    title: ReactNode;
    subtitle: string;
    logo: string;
};

export function HeaderBranding({title, subtitle, logo}: Props) {
    return (
        <div className="header-branding-card header-card">
            <img className="header-branding-logo" src={logo} alt="Logo"/>
            <div className="header-branding-text"> 
                <h1>{title}</h1>
                <p>{subtitle}</p>
            </div>
        </div>
    );
}