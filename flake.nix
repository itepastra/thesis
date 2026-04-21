{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixpkgs-unstable";
    typst = {
      url = "github:typst/typst-flake";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };
  outputs =
    { nixpkgs, typst, ... }:
    let
      allSystems = [
        "x86_64-linux" # 64-bit Intel/AMD Linux
        "aarch64-linux" # 64-bit ARM Linux
        "x86_64-darwin" # 64-bit Intel macOS
        "aarch64-darwin" # 64-bit ARM macOS
      ];
      forAllSystems =
        f:
        nixpkgs.lib.genAttrs allSystems (
          system:
          f {
            inherit system;
            typ = typst.packages.${system};
            pkgs = import nixpkgs { inherit system; };
          }
        );

    in
    {
      devShells = forAllSystems (
        {
          pkgs,
          typ,
          system,
          ...
        }:
        let
          tensornetwork-ng = pkgs.python3.pkgs.buildPythonPackage (finalAttrs: {
            pname = "tensornetwork-ng";
            version = "0.5.1";
            pyproject = true;

            src = pkgs.fetchPypi {
              pname = "tensornetwork_ng";
              inherit (finalAttrs) version;
              hash = "sha256-sSMHOWnDpUQLw2T3oMHkKLGdO3wMe0x+aqLpNr19uvM=";
            };

            build-system = [
              pkgs.python3.pkgs.setuptools
            ];

            dependencies = with pkgs.python3.pkgs; [
              graphviz
              h5py
              numpy
              opt-einsum
              scipy
            ];

            pythonImportsCheck = [
              "tensornetwork"
            ];

            passthru.updateScript = pkgs.nix-update-script { };

            meta = {
              description = "A high level tensor network API for accelerated tensor network calculations";
              homepage = "https://pypi.org/project/tensornetwork-ng";
              license = pkgs.lib.licenses.asl20;
            };
          });

          tensorcircuit = pkgs.python3.pkgs.buildPythonPackage (finalAttrs: {
            pname = "tensorcircuit-ng";
            version = "1.6.0";
            pyproject = true;

            src = pkgs.fetchPypi {
              pname = "tensorcircuit_ng";
              inherit (finalAttrs) version;
              hash = "sha256-G0KK05vUmm65b65XAP7sgwIGX0EpPqXG5OPW2I1L3w0=";
            };

            build-system = [
              pkgs.python3.pkgs.setuptools
            ];

            dependencies = with pkgs.python3.pkgs; [
              networkx
              numpy
              scipy
              tensornetwork-ng
            ];

            optional-dependencies = with pkgs.python3.pkgs; {
              cloud = [
                mthree
                qiskit
              ];
              jax = [
                jax
                jaxlib
              ];
              qiskit = [
                qiskit
                symengine
                sympy
              ];
              tensorflow = [
                tensorflow
              ];
              torch = [
                torch
              ];
            };

            pythonImportsCheck = [
              "tensorcircuit"
            ];

            meta = {
              description = "High performance unified quantum computing framework for the NISQ era";
              homepage = "https://pypi.org/project/tensorcircuit-ng";
              license = pkgs.lib.licenses.asl20;
              mainProgram = "tensorcircuit-ng";
            };
          });
        in
        {
          default = pkgs.mkShellNoCC {
            packages = [
              typ.default
              (pkgs.python3.withPackages (ppkgs: [
                ppkgs.numpy
                ppkgs.tqdm
                ppkgs.qiskit
                ppkgs.qiskit-aer
                ppkgs.matplotlib
                ppkgs.pytest
                ppkgs.pytest-xdist
                ppkgs.jax
                ppkgs.tensorflow
                ppkgs.keras
                ppkgs.pandas
                tensorcircuit
              ]))
            ];
          };
        }
      );
    };
}
