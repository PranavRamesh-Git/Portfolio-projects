function MarksAnalytics({overall,rankedList,subData}){
    return(
        <div className= "analytics">
            <div id="stats">
                <div id="overall">
                    <h2>OVERALL MARKS ANALYTICS: </h2>
                    <p>HIGHEST : {overall?.max_percent ?? "NA"}</p>
                    <p>LOWEST : {overall?.min_percent ?? "NA"}</p>
                    <p>AVERAGE : {overall?.avg_percent ?? "NA"}</p>
                </div>
                <div id="subWise">
                    <h2>SUBJECT WISE MARKS ANALYSIS</h2>
                    {Object.entries(subData).map(function([subject, data]) {
                        return (
                            <div key={subject}>
                                <h2>{subject}</h2>
                                <p>HIGHEST : {data.max_percent}</p>
                                <p>LOWEST : {data.min_percent}</p>
                                <p>AVERAGE : {data.avg_percent}</p>
                            </div>
                        );
                    })}
                </div>
                <div id="student-list">
                    {rankedList.map(function(ranked, index) {
                        return (
                            <div key={index}>
                                <p>
                                    {ranked.full_name} - {ranked.total_percentage}
                                    {" "}RANK: {ranked.rank}
                                </p>
                            </div>
                        );
                    })} 
                </div>  
            </div>                       
        </div>  
    );

}
export default MarksAnalytics;

