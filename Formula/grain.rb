class Grain < Formula
  include Language::Python::Virtualenv

  desc "CLI-first workflow toolkit for structured AI-assisted software development"
  homepage "https://github.com/Diwata-Labs/Grain"
  # Update the release artifact filename and sha256 when cutting a new formula.
  url "file://#{File.expand_path("../dist/grain-0.1.0.tar.gz", __dir__)}"
  sha256 "0ee0aa82310fb32faef7ba9ab08c8634ef4cbb5f1669c5723373b12df18c900d"
  license "MIT"

  depends_on "python@3.13"

  resource "click" do
    url "https://files.pythonhosted.org/packages/3d/fa/656b739db8587d7b5dfa22e22ed02566950fbfbcdc20311993483657a5c0/click-8.3.1.tar.gz"
    sha256 "12ff4785d337a1bb490bb7e9c2b1ee5da3112e94a8622f26a6c77f5d2fc6842a"
  end

  resource "PyYAML" do
    url "https://files.pythonhosted.org/packages/05/8e/961c0007c59b8dd7729d542c61a4d537767a59645b82a0b521206e1e25c2/pyyaml-6.0.3.tar.gz"
    sha256 "d76623373421df22fb4cf8817020cbb7ef15c725b9d5e45f17e189bfc384190f"
  end

  resource "networkx" do
    url "https://files.pythonhosted.org/packages/6a/51/63fe664f3908c97be9d2e4f1158eb633317598cfa6e1fc14af5383f17512/networkx-3.6.1.tar.gz"
    sha256 "26b7c357accc0c8cde558ad486283728b65b6a95d85ee1cd66bafab4c8168509"
  end

  resource "tree-sitter" do
    url "https://files.pythonhosted.org/packages/66/7c/0350cfc47faadc0d3cf7d8237a4e34032b3014ddf4a12ded9933e1648b55/tree-sitter-0.25.2.tar.gz"
    sha256 "fe43c158555da46723b28b52e058ad444195afd1db3ca7720c59a254544e9c20"
  end

  resource "tree-sitter-language-pack" do
    url "https://files.pythonhosted.org/packages/c1/83/d1bc738d6f253f415ee54a8afb99640f47028871436f53f2af637c392c4f/tree_sitter_language_pack-0.13.0.tar.gz"
    sha256 "032034c5e27b1f6e00730b9e7c2dbc8203b4700d0c681fd019d6defcf61183ec"
  end

  resource "tree-sitter-c-sharp" do
    url "https://files.pythonhosted.org/packages/22/85/a61c782afbb706a47d990eaee6977e7c2bd013771c5bf5c81c617684f286/tree_sitter_c_sharp-0.23.1.tar.gz"
    sha256 "322e2cfd3a547a840375276b2aea3335fa6458aeac082f6c60fec3f745c967eb"
  end

  resource "tree-sitter-embedded-template" do
    url "https://files.pythonhosted.org/packages/fd/a7/77729fefab8b1b5690cfc54328f2f629d1c076d16daf32c96ba39d3a3a3a/tree_sitter_embedded_template-0.25.0.tar.gz"
    sha256 "7d72d5e8a1d1d501a7c90e841b51f1449a90cc240be050e4fb85c22dab991d50"
  end

  resource "tree-sitter-yaml" do
    url "https://files.pythonhosted.org/packages/57/b6/941d356ac70c90b9d2927375259e3a4204f38f7499ec6e7e8a95b9664689/tree_sitter_yaml-0.7.2.tar.gz"
    sha256 "756db4c09c9d9e97c81699e8f941cb8ce4e51104927f6090eefe638ee567d32c"
  end

  def install
    virtualenv_install_with_resources
  end

  test do
    assert_match "grain, version", shell_output("#{bin}/grain --version")
    assert_match "Usage: grain init [OPTIONS]", shell_output("#{bin}/grain init --help")
  end
end
