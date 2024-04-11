CREATE TABLE tabFrequencia (
    idFreqData INT,
    dataLancamento DATETIME
);

CREATE TABLE tabFrequenciaSub (
    idFreq INT,
    freqID INT,
    aluno VARCHAR(255),
    turma VARCHAR(255),
    serie VARCHAR(255),
    dataFreq DATETIME,
    presente VARCHAR(3)
);

CREATE TABLE tbl_Atividades (
    -- Defina os campos da tabela conforme necessário
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255),
    descricao TEXT,
    dataInicio DATETIME,
    dataFim DATETIME,
    status VARCHAR(50)
);

CREATE TABLE Tbl_Cad_Escola (
    CodCadEscola INT PRIMARY KEY,
    Nome_Escola VARCHAR(255),
    nomeFantazia VARCHAR(255),
    Cidade_Escola VARCHAR(255),
    CEP_Escola VARCHAR(255),
    Bairro_Escola VARCHAR(255),
    Endereco_Escola VARCHAR(255),
    EntidadeMatenedora VARCHAR(255),
    Secretaria VARCHAR(255),
    CNPJ_Escola VARCHAR(255),
    CadastroMEC VARCHAR(255),
    LocalFotoEscola VARCHAR(255),
    NomeFotoEscola VARCHAR(255),
    Diretor VARCHAR(255),
    Secretario VARCHAR(255),
    LocalFotoAluno VARCHAR(255),
    Config_Servidor VARCHAR(255),
    Email_Escola VARCHAR(255),
    DocAut_dir VARCHAR(255),
    DocAut_Sec VARCHAR(255),
    Tipo_Escola VARCHAR(255),
    NivelEscolar VARCHAR(255)
);

CREATE TABLE audio_files (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    artist VARCHAR(255) NOT NULL,
    album VARCHAR(255),
    year INT,
    duration INT,
    file_path VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE tbl_CadAluno (
    CodCad_Aluno INT NOT NULL,
    NomeCad_Aluno VARCHAR(255) NOT NULL,
    DtNasc_Aluno DATETIME NOT NULL,
    Cidade_Aluno VARCHAR(255) NOT NULL,
    Endereco_Aluno VARCHAR(255) NOT NULL,
    Numero_Aluno VARCHAR(10) NOT NULL,
    naturaliadadeAluno VARCHAR(255) NOT NULL,
    CEP_Aluno VARCHAR(10) NOT NULL,
    bairro_Aluno VARCHAR(255) NOT NULL,
    Filiacao_Pai VARCHAR(255) NOT NULL,
    Filiacao_CelularPai VARCHAR(20) NOT NULL,
    Filiacao_Profissao_Pai VARCHAR(255) NOT NULL,
    Filiacao_RG_Pai VARCHAR(20) NOT NULL,
    Filiacao_GrauInst_Pai VARCHAR(255) NOT NULL,
    Filiacao_UF_Pai VARCHAR(2) NOT NULL,
    Filiacao_EnderecoPai VARCHAR(255) NOT NULL,
    Filiacao_Mae VARCHAR(255) NOT NULL,
    Filiacao_CelularMae VARCHAR(20) NOT NULL,
    Filiacao_Profissao_Mae VARCHAR(255) NOT NULL,
    Filiacao_RG_Mae VARCHAR(20) NOT NULL,
    Filiacao_GrauInst_Mae VARCHAR(255) NOT NULL,
    Filiacao_EnderecoMae VARCHAR(255) NOT NULL,
    Filiacao_UF_Mae VARCHAR(2) NOT NULL,
    CorRaca_Aluno VARCHAR(255) NOT NULL,
    Sexo_Aluno VARCHAR(255) NOT NULL,
    PortNecEspec VARCHAR(3) NOT NULL,
    DocAluno_Data_Registro DATETIME NOT NULL,
    DocAluno_Cartorio VARCHAR(255) NOT NULL,
    DocAluno_RG VARCHAR(20) NOT NULL,
    DocAluno_DataExpRG DATETIME NOT NULL,
    DocAluno_OrgaoEmissorRG VARCHAR(255) NOT NULL,
    DocAluno_UF_RG VARCHAR(2) NOT NULL,
    DocAluno_CPF VARCHAR(14) NOT NULL,
    DocAluno_CartaoSUS VARCHAR(20) NOT NULL,
    Celular_Aluno VARCHAR(20) NOT NULL,
    email_Aluno VARCHAR(255) NOT NULL,
    DocPendentesSimNao VARCHAR(1) NOT NULL,
    possuiConvenio VARCHAR(3) NOT NULL,
    DocAluno_NIS VARCHAR(11) NOT NULL,
    DocAluno_MatriculaCivil VARCHAR(255) NOT NULL,
    RespFinanceiro_NOME VARCHAR(255) NOT NULL,
    PRIMARY KEY (CodCad_Aluno)
);

CREATE TABLE tbl_CadAnoLetivo (
    ID_AnoLetivo INT NOT NULL,
    Nome_AnoLetivo VARCHAR(255) NOT NULL,
    PRIMARY KEY (ID_AnoLetivo)
);

CREATE TABLE tbl_CadAnos (
    ID_Ano INT PRIMARY KEY,
    Nome_Ano VARCHAR(255)
);

CREATE TABLE tbl_CadNivelEscolaridade (
    ID_Nivel INT PRIMARY KEY,
    Nome_Nivel VARCHAR(255)
);

CREATE TABLE tbl_CadSerie (
    ID_Serie INT PRIMARY KEY,
    Nome_Serie VARCHAR(255),
    nivelEscolar VARCHAR(255)
);

CREATE TABLE tbl_CadTipoResultado (
    ID_Resultado INT PRIMARY KEY,
    Nome_Resultado VARCHAR(255)
);

CREATE TABLE tbl_CadTurmas (
    ID_Turmas INT PRIMARY KEY,
    COD_Escola INT,
    Nome_Turmas VARCHAR(255)
);

CREATE TABLE tbl_CadTurnos (
    ID_Turno INT PRIMARY KEY,
    Nome_Turno VARCHAR(255),
    Horario_Turno VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS tbl_cep_brasil (
    cep VARCHAR(8) PRIMARY KEY,
    cidade VARCHAR(255) NOT NULL,
    estado CHAR(2) NOT NULL,
    localidade_nao_subordinada VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS tbl_end_bairros (
    id INT PRIMARY KEY,
    nome_bairro VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS tbl_end_ruas (
    codigo INT PRIMARY KEY,
    nome_rua VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS tbl_func_det (
    id_fun INT PRIMARY KEY,
    cod_escola INT,
    dt_cad DATE,
    nome_func VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS tbl_ocorrencias (
    codigo INT PRIMARY KEY,
    cod_escola INT,
    cod_aluno INT,
    cod_matricula INT,
    ano_letivo INT,
    data_ocorrencia DATETIME,
    relato_ocorrencia TEXT,
    ano_escolar VARCHAR(255),
    turma VARCHAR(255),
    ato_indisciplinar TEXT,
    nome_declarante VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS tbl_transp_escolar (
    codigo INT PRIMARY KEY,
    rota_numero VARCHAR(255),
    prop_nome VARCHAR(255),
    prop_fone VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS tbl_transp_escolar_rotas (
    codigo INT PRIMARY KEY,
    rota_numero VARCHAR(255),
    rota_nome VARCHAR(255),
    rota_final VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS tbl_cad_motivo_saida (
    id_motivo_saida INT PRIMARY KEY,
    motivo_saida VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS tbl_det_matricula (
    id_mat_alunos INT PRIMARY KEY,
    cod_escola INT,
    cod_aluno_det INT,
    dt_matricula DATE,
    ano_letivo INT,
    serie_ano_escolar VARCHAR(255),
    turma VARCHAR(255),
    nivel VARCHAR(255),
    turno VARCHAR(255),
    proced_aluno VARCHAR(255),
    resultado VARCHAR(255),
    dt_alteracao DATETIME
);

CREATE TABLE IF NOT EXISTS tbl_series (
    id INT PRIMARY KEY,
    nserie VARCHAR(255)
);
