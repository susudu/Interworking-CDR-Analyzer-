# Interworking CDR Analyzer
This solution covers the CDR volume trend views, its detection of anomalies in input CDR and File level in Wholesale Business using arima model. 

The solution includes daily monthly, and yearly views of related business CDR trends. 

The CDR node wise trend views, System wise total CDR volume views, so this can be used to analyze the volume metrics.  

The module also discovers all possible anomalies of above 3 categories as described. 

In addition, the program will also initiate RPA executions up on the anomaly detected by model, take actions and reports the incident to the respective Operation team over Mail, and Mobile SMS Alert. 

This covers twenty-eight anomaly detection points across the systems, and hundred and seven actions against the detected anomalies over RPA process, as well as 28 daily dashboard views. 

## Design

Get thorough understanding of what need to be covered up from the business perspective. 

Looking for what data we do have and what we actually need and check whether its clean to be used. 

Preparing and organizing data as selecting, cleansing, constructing, integrating, & formatting for data modeling. 

Choosing what modeling techniques should we applied and generate test design, build the model, and assess the model. 

Visualizing the output from built model as behavior of data trends in daily basis plots,  monthly basis plots, and generating an informative mail as a daily dashboard. 

Meanwhile, logically identifying anomalies of each data trends, and alerting detected anomalies via SMS, and email by assigning unique incident number for each alert, as it makes ease to be followed up the case to desired channel.  

Analyzing detected anomalies up to every possible point and it will provide detailed reports with the findings relative to the incident. Then it passes to respective operation team to investigate and take actions over the incident. 

Currently the program handles up to 3 levels of post execution tasks based on the findings of each level. 

![image](https://user-images.githubusercontent.com/9928449/173234472-1dd7272d-c1dc-43bd-a700-8dd73697c491.png)

## Logical Analysis and guide to smart workflow over RPA 

After identifying an anomaly, we were keen to take one step ahead to the analysis and take actions as an RPA process. 

This PRA execution in each 3 level will cover all possible causes which lead to have any drop or hike in CDR and File flows.

![image](https://user-images.githubusercontent.com/9928449/173234631-0fa97ca7-963b-469d-a42b-9417dddf0b15.png)


