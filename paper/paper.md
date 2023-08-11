---
title: 'TOMRAP: Tool for Multihazard Risk Analysis in Python'
tags:
  - Python
  - multihazrd-risk
  - geology
authors:
  - name: Winson
    orcid: 0000-0002-6420-1042
    affiliation: 1
  - name: Valters
    orcid: 0000-0002-4562-3944
    corresponding: true # (This is how to denote the corresponding author)
    affiliation: 1
  - name: Smith
    orcid: 0000-0003-3287-6974
    affiliation: 1
  - name: Leeming
    affiliation: 1
    orcid: 0000-0001-9724-2855
affiliations:
 - name: British Geological Survey, United Kingdom
   index: 1

date: 04 July 2023
bibliography: paper.bib


---

# Summary

Multihazards are defined as the major multiple hazards that an area might face and the specific context in which they occur, which may be simultaneously, cascadingly, or cumulatively through time (UNDRR, 2017). TOMRAP is an open-source python toolbox capable of generating a compounding / coincident multi-hazard risk assessment at national scale, incorporating any available hazard and exposure data with user defined weighting factors to reflect the changing vulnerability of building stock to various hazards. 

# Statement of need

Globally individual and interrelated hazards have the potential to result in large socio-economic losses (Tilloy et al., 2019). There is a growing body of literature highlighting the need to move from single risk to multihazard risk assessment (for example: Kappes et al., 2012a; Gill and Malamund, 2016; Zschau, 2017; Ciurean et al., 2018; Tilloy et al., 2019; De Angeli et al., 2022; Ward et al., 2022). Past studies have investigated a range of potential methods for modelling these interactions, from purely qualitative to purely quantitative approaches. These include tools such as: Hazard Wheels (Rosendahl et al., 2015), Hazard Matrices (Gill and Malamund, 2014, Kappes et al., 2012a), Hazard / Risk Indices (Kappes et al., 2012b) and Probabilistic frameworks (Mignan et al., 2014). With more quantitative models requiring increasingly dense inventories of events to support the appropriate level of statistical analysis. These approaches vary, but fundamentally they attempt to quantify the nature, intensity and return period of specific hazards. Each single hazard has a different standardised unit of measurement for magnitude, and it is this lack of common standardisation that can make multi-hazard assessments complex (Kappes et al., 2012a). In practice multi-hazard assessments are complicated by the differences between hazard characteristics and therefore the methods used to analyse them and that the impacts on exposure can be different for differing hazards and occasionally opposing (Kappes et al., 2012a). 

As part of the UK Space Agency’s International Partnership Program funded METEOR project, we developed a framework for modelling multihazard risk, which aggregates hazard, building exposure and vulnerability data to produce a national level semi-quantitative risk assessment.  This framework allows the aggregation of various probabilistic and inventory-based susceptibility and hazard assessments (for earthquake, volcano, flood and landslide), with satellite derived building exposure data and an assessment of building vulnerability, defined either by the input of fragility failure curves or through expertly elicited weighting factors.  This methodology can therefore be adapted dependant on what data is available to the end users and can be pushed to either a more qualitative or more quantitative output, as the data supports.


# Modelling Multihazard Risk

TOMRAP is a modelling toolbox written in Python that: 1) Creates an index value to allow for the combination of hazard footprints for 4 natural hazards, 2) Identifies the factors that affect the exposure and vulnerability of buildings to these specific hazards, 3) Calculates the vulnerability of individual buildings within hazard zones, 4) Applies weights for each building type to express the potential vulnerability of individual buildings to a specific hazard to generate relative single hazard vulnerability maps and then 5) Combines these single hazard ‘relative vulnerability maps’ to generate a multi-hazard vulnerability map which is weighted to reflect single hazard frequency / magnitude relationships. The basic structure of the modelling framework can be seen in \autoref{fig:Flowchart}.

![Generic workflow for the TOMRAP tool. The toolbox aggregates multiple hazard layers with exposure data, that can be weighted over a range of hazard specific vulnerabilities at a pixel scale. This process creates relative vulnerability outputs for each hazard, a weighted sum of these outputs reflects the frequency magnitude distribution of the single hazards and generates a multi-hazard risk product. \label{fig:Flowchart}](Flowchart.png)

The hazard map for a particular location, i, is a sum over individual hazards and can be defined as such:

$$
H_i = \sum_{k \in K} \beta_kh_{ki}
$$

where the map value for each hazard is given by: 

$$
h_ki = \Sigma_{l \in L_k} \alpha_lg_{li} (\Sigma_{m \in M} \gamma_{ml}b_{mi}).
$$

Where: $H_i$ is the final hazard map at location _i_, _K_ is the set of hazards combined in the final map, for example volcanic, seismic and flooding, $\Beta_k$ is the weight of hazard _k_, where $\Sigma_{k \in K}\Beta_{k} = 1$, $h_{ki}$ is the value of the hazard _k_ at location _i_, $L_k$ is the set of sub-classes within a hazard, for example pluvial and fluvial flooding. (If a hazard does not have sub-classes $L_k$ only has one entry and the sum is over one class), $\alpha_l$  is the weight of sub-class _l_, where  $\Sigma_{l \in L_k} \alpha_l = 1$, $g_{li}$ is the hazard index for sub-class _l_ at location _i_, _M_ is the set of building classes, for example "CR/LFM/HBET:1,3", "S", $\gamma_{ml}$ is the building weight for building class _m_ and sub-class _l_, $b_{mi}$ is the proportion of building type m at location _i_, where $\Sigma_{m \in M}b_{mi} =  1$ for all locations _i_.

![Map of multihazrd risk index for the test country of Tanzania. This output combines hazard data for earthquake, flood and volcanic hazard and combines it with building exposure, weighted for hazard specific vulnerabilities. Separate hazards are then weighted together to generate a multihazard risk map.\label{fig:Tanzania}](Tanzania.png)


The TOMRAP software package is released under an open source licence and distributed via GitHub. The interface to the software is via running a command line script that invokes the TOMRAP code, and a config file supplied allows the user to configure the input data sources, and any weighting factors. The sofware can also be configured to calculate weighting factors for hazards based on the user supplying vulnerability curve data (\autoref{fig:Vuln_curve}) The config file also allows the user to determine which output figures are produced from the analysis. (E.g. \autoref{fig:Tanzania})

![Ilustriative diagram of how a supplied vulnerabiltiy curve or curves for a each building type can be used to determine the weighting factor/vulnerability multiplier based on a given hazard intensity. The vulnerability curve data is supplied in csv format.\label{fig:Vuln_curve}](Vuln_curve.png)

TOMRAP was designed to be used by decision makers and stakeholders who are responsible for pre-positioning of resources prior to a disaster event and for those who are assessing the potential efficacy of interventions such as adapting building codes. The products from this toolbox are intended to provide guidance on the relative risk from multihazards at a national scale. It is important to note that any uncertainty associated with the input datasets is likely to be compounded by the aggregation of data within the model. It is therefore important to bear in mind that any data generated by this tool should be assessed for uncertainty. Methodologies for this are outlined in the publications attributed to the METEOR project (Winson et al., 2020) as are all of the data sets created to support it (https://meteor-project.org/ and https://maps.meteor-project.org/). Risk products generated by this tool should not be consider absolute risk assessments but rather a measure of the relative risk of areas in the context of specific natural hazards. (E.g. \autoref{fig:Tanzania})

# Acknowledgements

The research leading to the creation of this tool has been supported by: co-funding from the second iteration of the UK Space Agency’s (UKSA) International Partnership Programme (IPP), through the Modelling Exposure Through Earth Observation Routines (METEOR) project, UK National Capability Funding (Innovation Flexible Fund programme / Overseas Disaster Assistance Programme). We would like to thank a number of colleagues for creating the data sets that we used to inform this tool: ImageCat Inc, GEM Foundation (Global Earthquake Model), National Society for Earthquake Technology (NSET), Fathom, Prime Minister’s Office of Tanzania (Policy, Parliament and Coordination); Disaster Management Department, Humanitarian OpenStreetMap Team.

# References

EXAMPLE  of citing the `Astropy` package [@astropy] (`astropy.units` and
`astropy.coordinates`).

Ciurean, R., Gill, J., Reeves, H. J., O’Grady, S., and Aldridge, T.: Review of environmental multi-hazards research and risk assessments, OR/18/057, British Geological Survey, Nottingham, UK, http://nora.nerc.ac.uk/id/eprint/524399/1/OR18057.pdf (last access: 19 July 2023), 2018.

De Angeli, S., Malamud, B.D., Rossi, L., Taylor, F.E., Trasforini, E. and Rudari, R., 2022. A multi-hazard framework for spatial-temporal impact analysis. International Journal of Disaster Risk Reduction, 73, p.102829.

Gill, J.C. and Malamud, B.D., 2014. Reviewing and visualizing the interactions of natural hazards. Reviews of Geophysics, 52(4), pp.680-722.

Gill, J. C. and Malamud, B. D. 2016. Hazard interactions and interaction networks (cascades) within multi-hazard methodologies, Earth Syst. Dynam., 7, 659–679, https://doi.org/10.5194/esd-7- 659-2016.

Kappes, M.S., Keiler, M., von Elverfeldt, K. and Glade, T., 2012a. Challenges of analyzing multi-hazard risk: a review. Natural hazards, 64, pp.1925-1958.

Kappes, M.S., Papathoma-Koehle, M. and Keiler, M., 2012b. Assessing physical vulnerability for multi-hazards using an indicator-based methodology. Applied Geography, 32(2), pp.577-590.

Mignan, A., Wiemer, S. and Giardini, D., 2014. The quantification of low-probability–high-consequences events: part I. A generic multi-risk approach. Natural Hazards, 73, pp.1999-2022.

Rosendahl Appelquist, L. and Halsnæs, K., 2015. The Coastal Hazard Wheel system for coastal multi-hazard assessment & management in a changing climate. Journal of coastal conservation, 19, pp.157-179.

Tilloy, A., Malamud, B.D., Winter, H. and Joly-Laugel, A., 2019. A review of quantification methodologies for multi-hazard interrelationships. Earth-Science Reviews, 196, p.102881.

UNDRR: Terminology for Disaster Risk Reduction, UNDRR, Geneva, Switzerland, https://www.undrr.org/terminology (last access: 19 July 2023), 2017.

UNDRR: GAR 2022. Global Assessment Report on Disaster Risk Reduction 2022: Our World at Risk: Transforming Governance for a Resilient Future. United Nations Office for Disaster Risk Reduction, Geneva, Switzerland, https://www.undrr.org/gar2022-our-world-risk-gar (last access: 19 July 2023).

Ward, P.J., Daniell, J., Duncan, M., Dunne, A., Hananel, C., Hochrainer-Stigler, S., Tijssen, A., Torresan, S., Ciurean, R., Gill, J. and Sillmann, J., 2022. Invited perspectives: A research agenda towards disaster risk management pathways in multi-(hazard-) risk assessment. Natural Hazards and Earth System Science, 22(4), pp.1487-1497.

Zschau, J.: Where are we with multihazards, multirisks assessment capacities?, in: Science for disaster risk management 2017: knowing better and losing less, edited by: Poljansek, K., Marin Ferrer, M., 

De Groeve, T., and Clark, I., European Union, Brussels, Belgium, https://drmkc.jrc.ec.europa.eu/knowledge/ science-for-drm/science-for-disaster-risk-management-2017 (last access: 19 July 2023), 2017.


# Citations

Citations to entries in paper.bib should be in
[rMarkdown](http://rmarkdown.rstudio.com/authoring_bibliographies_and_citations.html)
format.

If you want to cite a software repository URL (e.g. something on GitHub without a preferred
citation) then you can do it with the example BibTeX entry below for @fidgit.

For a quick reference, the following citation commands can be used:
- `@author:2001`  ->  "Author et al. (2001)"
- `[@author:2001]` -> "(Author et al., 2001)"
- `[@author1:2001; @author2:2001]` -> "(Author1 et al., 2001; Author2 et al., 2002)"

# Figures

Figures can be included like this:
![Caption for example figure.\label{fig:example}](figure.png)
and referenced from text using \autoref{fig:example}.

Figure sizes can be customized by adding an optional second parameter:
![Caption for example figure.](figure.png){ width=20% }

# Acknowledgements

We acknowledge contributions from

# References
