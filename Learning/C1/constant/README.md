/*--------------------------------*- C++ -*----------------------------------*\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     | Website:  https://openfoam.org
    \\  /    A nd           | Version:  13
     \\/     M anipulation  |
\*---------------------------------------------------------------------------*/
FoamFile
{
    format      ascii;
    class       dictionary;
    location    "constant";
    object      physicalProperties;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

// Apparently this solver is better suited for tracking the movement of air when heating and cooling matter.

thermoType
{
    // Thermodynamics package based on density (rho) and enthalpy/internal energy style thermodynamics (he). Suitable for compressible flows.
    type            heRhoThermo; 

    // One single species mixture.
    mixture         pureMixture; 

    // Viscosity-related properties do not vary with temperature.
    transport       const; 

    // Constant specific heat.
    thermo          hConst; 

    // The air obeys the ideal gas law.
    equationOfState perfectGas; 

    // Uses the standard species description block, as described below.
    specie          specie; 

    // Thermal energy is tracked relative to a reference state. This is important if there are expected temperature variations. 
    energy          sensibleEnthalpy; 
}

pRef            100000; // Reference pressure of 100,000 P or 1 bar.

mixture
{
    specie
    {
        molWeight       28.9; // Approximate molecular weight of air (28.9 g/mol).
    }
    thermodynamics
    {
        Cp              1000; // Constant-pressure specific heat (1000 J/(kg*K)).
        hf              0; // Heat of formation of zero. Typical for non-reacting air case.
    }
    transport
    {
        mu              1.8e-05; // Dynamic visocity of 1.8 * 10^-5 Pa*s, typical for air.
        Pr              0.7; // Prandtl number of 0.7, typical for air.
    }
}


// ************************************************************************* //