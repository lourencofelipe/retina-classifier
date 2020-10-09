let base64Image;

const linhaTabela = () => $(document.querySelector("#table > tbody")).find('tr');

const limparCampos = () => {
    let linhasTabela = linhaTabela();

    $("#retinopatia-positivo").text("");
    $("#retinopatia-negativo").text("");
    linhasTabela.find('td:eq(0)').html("");
    linhasTabela.find('td:eq(1)').text("");
    linhasTabela.find('td:eq(2)').text("");
    linhasTabela.find('td:eq(3)').text("");

    $('#table-display').css("display", "none");
}

const alertaFormatoImagemInvalido = () => {
    swal({
        title: "Atenção!",
        text: "A extensão do arquivo não é válida!",
        icon: "error",
        button: "ok",
    });
    $('#imagem-selecionada').attr("src", "");
    $('#imagem-selecionada').css("display", "none");
    $('#imagem-seletor').val('');
}

const atribuirValorImagemValido = (dataURL) => {
    $('#imagem-selecionada').attr("src", dataURL);
    base64Image = dataURL.split("base64,")[1];
    $('#imagem-selecionada').css("display", "block");
}

const preencheTabela = (response) => {
    let linhasTabela = linhaTabela();
    linhasTabela.find('td:eq(0)').html(`<img src="${$("#imagem-selecionada").attr("src")}" class="img-fluid img-thumbnail" alt="Análise" style="background-color:#81C784;" />`);
    let descricaoResultado = linhasTabela.find('td:eq(1)');
    let precisaoResultado = linhasTabela.find('td:eq(2)');
    let sintomatica = response.predicao.classeImagem == 1;
    let assintomatica = response.predicao.classeImagem == 0;

    if (sintomatica) {
        descricaoResultado.text("Positivo");
        precisaoResultado.text(Number(response.predicao.sintomatica).toFixed(3) + "%");
    } else if (assintomatica) {
        descricaoResultado.text("Negativo");
        precisaoResultado.text(Number(response.predicao.assintomatica).toFixed(3) + "%");
    }

    linhasTabela.find('td:eq(3)').text(formatarData() + ' ' + formatarHorario());
    $('#table-display').css("display", "block");
}

const formatarData = () => {
    let data = new Date()
    const formatoData = {
        dia: '2-digit',
        mes: '2-digit',
        ano: 'numeric'
    };

    let dataFormatada = data.toLocaleDateString("pt-br", formatoData);

    return dataFormatada;
}

const formatarHorario = () => {
    let data = new Date();
    const formatoHorario = {
        hora: '2-digit',
        minutes: '2-digit',
        seconds: '2-digit'
    };

    let horarioFormatado = data.toLocaleTimeString("pt-br", formatoHorario);

    return horarioFormatado;
}

const habilitarBotaoAnalise = () => $("#classificarImagem-button").prop('class', 'btn text-white btn-primary mr-2');

const habilitarBotaoExcluir = () => $("#excluirImagem-button").prop('class', 'btn btn-outline-danger');

const desabilitarBotaoAnalise = () => $("#classificarImagem-button").prop('class', 'btn text-white btn-primary mr-2 disabled');

const desabilitarBotaoExcluir = () => $("#excluirImagem-button").prop('class', 'btn btn-outline-danger disabled');

const limparCampoImagem = () => $("#imagem-selecionada").prop('src', '');

const imprimirResultado = () => {

    let tabela = document.getElementById('table');

    let janela = window.open('', '', 'height=700,width=1200');

    let style = "<style>";
    style = style + "table {width: 90%; font: 17px Calibri;}";
    style = style + "table, th, td {border-bottom: solid 1px #DDD; text-align:left;border-top: solid 1px #DDD; border-collapse: collapse;";
    style = style + "padding: 2px 3px; }";
    style = style + "img {width:150px;";
    style = style + "</style>";
    janela.document.write(style);

    janela.document.write(tabela.outerHTML);
    janela.document.close();
    janela.print();
}

const excluirImagem = () => {
    limparCampoImagem();
    desabilitarBotaoAnalise();
    desabilitarBotaoExcluir();
    limparCampos();
}

const validaExtensao = (dataURL) => {
    let extensaoValida = false;
    let extensaoUrl = dataURL.split("base64,")[0];
    let png = extensaoUrl.indexOf('png') != -1;
    let jpg = extensaoUrl.indexOf('jpg') != -1;
    let jpeg = extensaoUrl.indexOf('jpeg') != -1;

    if (png || jpg || jpeg)
        extensaoValida = true;
    else
        extensaoValida = false;

    return extensaoValida;
}

const informacoesProjeto = () => $.post("https://retinaclassifier.herokuapp.com/informacoes",
    () => window.location.href = "https://retinaclassifier.herokuapp.com/informacoes");

$("#local-imagem").click(() => $("#imagem-seletor").trigger('click'));

$("#imagem-seletor").change(() => {
    let reader = new FileReader();

    reader.onload = (e) => {
        let dataURL = reader.result;

        if (validaExtensao(dataURL)) {
            atribuirValorImagemValido(dataURL);
            habilitarBotaoAnalise();
            habilitarBotaoExcluir();
        } else
            alertaFormatoImagemInvalido();
    }
    reader.readAsDataURL($("#imagem-seletor")[0].files[0]);
    limparCampos();
});

$("#classificarImagem-button").click(() => {

    if ($("#imagem-selecionada").attr("src") !== "") {
        let message = {
            image: base64Image
        }

        $.post("https://retinaclassifier.herokuapp.com/predict", JSON.stringify(message), (response) => {
            if (response.predicao.classeImagem !== undefined || response.predicao.classeImagem !== null)
                preencheTabela(response);
        });
    }
});