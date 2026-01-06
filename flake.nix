{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixpkgs-unstable";
    typst = {
      url = "github:typst/typst";
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
            typst = typst.packages.${system};
            pkgs = import nixpkgs { inherit system; };
          }
        );
    in
    {
      devShells = forAllSystems (
        {
          pkgs,
          typst,
          system,
          ...
        }:
        {
          default = pkgs.mkShellNoCC {
            packages = [
              pkgs.typst
              (pkgs.python3.withPackages (ppkgs: [
                ppkgs.numpy
                ppkgs.tqdm
              ]))
            ];
          };
        }
      );
    };
}
