type Props = {
    intro: string;
    description: string;
};

export function AppDescription({intro, description}: Props) {
    return(
        <div className="app-description-card card">
            <h1><span className="bold-text">{intro}</span></h1>
            <hr className="line-divider"/>
            <p>{description}</p>
        </div>
    );
}