type Props = {
    title: string;
    subtitle: string;
    logo: string;
};

export function HeaderBranding({title, subtitle, logo}: Props) {
    return (
        <div className="header-branding-card header-card">
            <div className="header-branding-card-top">
                <img className="header-branding-logo" src={logo} alt="Logo"/>
                <h1 className="header-branding-title">{title}</h1>
            </div>
            <p className="header-branding-subtitle">{subtitle}</p>
        </div>
    );
}