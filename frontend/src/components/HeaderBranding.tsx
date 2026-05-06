type Props = {
    title: string;
    subtitle: string;
};

export function HeaderBranding({title, subtitle}: Props) {
    return (
        <div className="header-branding-card header-card">
            <div className="header-branding-text"> 
                <h1 className="header-branding-title">{title}</h1>
                <p className="header-branding-subtitle">{subtitle}</p>
            </div>
        </div>
    );
}