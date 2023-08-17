---
title: 'TOMRAP: Tool for Multihazard Risk Analysis in Python'
tags:
  - Python
  - multihazrd-risk
  - geology
authors:
  - name: Winson, Annie E. G.
    orcid: 0000-0002-6420-1042
    affiliation: 1
  - name: Valters, Declan A.
    orcid: 0000-0002-4562-3944
    corresponding: true # (This is how to denote the corresponding author)
    affiliation: 1
  - name: Smith, Kay B.
    orcid: 0000-0003-3287-6974
    affiliation: 1
  - name: Leeming, Kathryn A.
    affiliation: 1
    orcid: 0000-0001-9724-2855
affiliations:
 - name: British Geological Survey, Keyworth, Nottingham, NG12 5GG, United Kingdom
   index: 1

date: 15 August 2023
bibliography: tomrap.bib


---

# Summary

Multihazards are defined as the major multiple hazards that an area might face and the specific context in which they occur, which may be simultaneously, cascadingly, or cumulatively through time [@undrr17; @undrr22]. TOMRAP is an open-source python toolbox capable of generating a compounding / coincident multi-hazard risk assessment at national scale, incorporating any available hazard and exposure data with user defined weighting factors to reflect the changing vulnerability of building stock to various hazards. 

# Statement of need

Globally individual and interrelated hazards have the potential to result in large socio-economic losses [@tmwj19]. There is a growing body of literature highlighting the need to move from single risk to multihazard risk assessment [@kkvg12; @kpk12; @gm16; @zschau2017; @cgroa18; @tmwj19; @dmrttr22; @wdddhhttcgs22]. Past studies have investigated a range of potential methods for modelling these interactions, from purely qualitative to purely quantitative approaches. These include tools such as: Hazard Wheels [@ra2015], Hazard Matrices [@gm14; @kpk12], Hazard / Risk Indices [@kkvg12] and Probabilistic frameworks [@mwg14]. With more quantitative models requiring increasingly dense inventories of events to support the appropriate level of statistical analysis. These approaches vary, but fundamentally they attempt to quantify the nature, intensity and return period of specific hazards. Each single hazard has a different standardised unit of measurement for magnitude, and it is this lack of common standardisation that can make multi-hazard assessments complex [@kkvg12]. In practice multi-hazard assessments are complicated by the differences between hazard characteristics and therefore the methods used to analyse them and that the impacts on exposure can be different for differing hazards and occasionally opposing [@kkvg12]. 

As part of METEOR project, funded through the UK Space Agency’s International Partnership Program, we developed a framework for modelling multihazard risk, which aggregates hazard, building exposure and vulnerability data to produce a national level semi-quantitative risk assessment.  This framework allows the aggregation of various probabilistic and inventory-based susceptibility and hazard assessments (developed for earthquake, volcano, flood and landslide), with satellite derived building exposure data and an assessment of building vulnerability, defined either by the input of fragility failure curves or through expertly elicited weighting factors.  This methodology can therefore be adapted dependant on what data is available to the end users and can be pushed to either a more qualitative or more quantitative output, as the data supports.


# Modelling Multihazard Risk

TOMRAP is a modelling toolbox written in Python that: 1) Creates an index value to allow for the combination of hazard footprints for 4 natural hazards, 2) Identifies the factors that affect the exposure and vulnerability of buildings to these specific hazards, 3) Calculates the vulnerability of individual buildings within hazard zones, 4) Applies weights for each building type to express the potential vulnerability of individual buildings to a specific hazard to generate relative single hazard vulnerability maps and then 5) Combines these single hazard ‘relative vulnerability maps’ to generate a multi-hazard vulnerability map which is weighted to reflect single hazard frequency / magnitude relationships. The basic structure of the modelling framework can be seen in \autoref{fig:Flowchart}.

![Generic workflow for the TOMRAP tool. The toolbox aggregates multiple hazard layers with exposure data, that can be weighted over a range of hazard specific vulnerabilities at a pixel scale. This process creates relative vulnerability outputs for each hazard, a weighted sum of these outputs reflects the frequency magnitude distribution of the single hazards and generates a multi-hazard risk product. \label{fig:Flowchart}](Flowchart.png)

The hazard map for a particular location, i, is a sum over individual hazards and can be defined as such:

$$
H_i = \sum_{k \in K} \beta_kh_{ki}
$$

where the map value for each hazard is given by: 

$$
h_{ki} = \Sigma_{l \in L_k} \alpha_lg_{li} (\Sigma_{m \in M} \gamma_{ml}b_{mi}).
$$

Where: $H_i$ is the final hazard map at location _i_, _K_ is the set of hazards combined in the final map, for example volcanic, seismic and flooding, $\Beta_k$ is the weight of hazard _k_, where $\Sigma_{k \in K}\Beta_{k} = 1$, $h_{ki}$ is the value of the hazard _k_ at location _i_, $L_k$ is the set of sub-classes within a hazard, for example pluvial and fluvial flooding. (If a hazard does not have sub-classes $L_k$ only has one entry and the sum is over one class), $\alpha_l$  is the weight of sub-class _l_, where  $\Sigma_{l \in L_k} \alpha_l = 1$, $g_{li}$ is the hazard index for sub-class _l_ at location _i_, _M_ is the set of building classes,  $\gamma_{ml}$ is the building weight for building class _m_ and sub-class _l_, $b_{mi}$ is the proportion of building type m at location _i_, where $\Sigma_{m \in M}b_{mi} =  1$ for all locations _i_.

![Map of multihazrd risk index for the test country of Tanzania. This output combines hazard data for earthquake, flood and volcanic hazard and combines it with building exposure, weighted for hazard specific vulnerabilities. Separate hazards are then weighted together to generate a multihazard risk map.\label{fig:Tanzania}](Tanzania.png)


The TOMRAP software package is released under an open source licence and distributed via GitHub. The interface to the software is via running a command line script that invokes the TOMRAP code, and a config file supplied allows the user to configure the input data sources, and any weighting factors. The sofware can also be configured to calculate weighting factors for hazards based on the user supplying vulnerability curve data (\autoref{fig:Vuln_curve}) The config file also allows the user to determine which output figures are produced from the analysis. (E.g. \autoref{fig:Tanzania})

![Illustrative diagram of how a supplied vulnerability curve or curves for a each building type can be used to determine the weighting factor/vulnerability multiplier based on a given hazard intensity. The vulnerability curve data is supplied in csv format.\label{fig:Vuln_curve}](Vuln_curve.png)

TOMRAP was designed to be used by decision makers and stakeholders who are responsible for pre-positioning of resources prior to a disaster event and for those who are assessing the potential efficacy of interventions such as adapting building codes. The products from this toolbox are intended to provide guidance on the relative risk from multihazards at a national scale. It is important to note that any uncertainty associated with the input datasets is likely to be compounded by the aggregation of data within the model. It is therefore important to bear in mind that any data generated by this tool should be assessed for uncertainty. Methodologies for this are outlined in the publications attributed to the METEOR project [@wjgs20] as are all of the data sets created to support it (https://meteor-project.org/ and https://maps.meteor-project.org/). Risk products generated by this tool should not be considered absolute risk assessments but rather a measure of the relative risk of areas in the context of specific natural hazards. (E.g. \autoref{fig:Tanzania})

# Acknowledgements

The research leading to the creation of this tool has been supported by: co-funding from the second iteration of the UK Space Agency’s (UKSA) International Partnership Programme (IPP), through the Modelling Exposure Through Earth Observation Routines (METEOR) project, and the UK National Capability Funding (Innovation Flexible Fund programme / Overseas Disaster Assistance Programme). We would like to thank a number of colleagues for creating the data sets that we used to inform this tool: ImageCat Inc, GEM Foundation (Global Earthquake Model), National Society for Earthquake Technology (NSET), Fathom, Prime Minister’s Office of Tanzania (Policy, Parliament and Coordination); Disaster Management Department, and the Humanitarian OpenStreetMap Team.

# References


