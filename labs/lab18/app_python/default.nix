{ pkgs ? import <nixpkgs> {} }:

let
  pythonEnv = pkgs.python313.withPackages (ps: with ps; [
    fastapi
    uvicorn
    prometheus-client
  ]);
in
pkgs.stdenv.mkDerivation {
  pname = "devops-info-service";
  version = "1.0.0";
  src = builtins.filterSource
    (path: type:
      let base = builtins.baseNameOf path;
      in base != "result" && base != ".DS_Store")
    ./.;

  buildInputs = [ pythonEnv ];

  installPhase = ''
    mkdir -p $out/bin $out/share

    cat > $out/bin/devops-info-service << 'SCRIPT'
#!/usr/bin/env bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
exec ${pythonEnv}/bin/python3 "''${SCRIPT_DIR}/../share/app.py" "$@"
SCRIPT

    chmod +x $out/bin/devops-info-service
    cp app.py $out/share/app.py
  '';
}
