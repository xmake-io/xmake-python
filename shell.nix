{
  pkgs ? import <nixpkgs> { },
}:

with pkgs;
mkShell {
  name = "xmake-python";
  buildInputs = [
    xmake

    (python3.withPackages (
      p: with p; [
        uv
        pytest
      ]
    ))
  ];
}
