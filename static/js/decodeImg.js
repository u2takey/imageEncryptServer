

//生成解密用的key baseKey 为固定key privatekey为用户key
function getKey(privateKey){
	var result = CryptoJS.MD5(privateKey).toString();
	for (var i = 0; i < 20; ++i) {
		result += CryptoJS.MD5(result).toString();
	};
	return result;
}

function decodeImg(imgdata, keyData, ctx){
    
    var w = imgdata.width;
	var h = imgdata.height;
    var DefaultH = 720.0;
    var DefaultKeyFactor = 8;

    var myImageData1 = ctx.createImageData(w, h);
    var myImageData2 = ctx.createImageData(w, h);
    
    //y trans
    var pixOff = 0;
    var newOff = 0;
    var key = 0;
    var newx = 0;
    var newy = 0;
    
    for(var y = 0;y< h;y++)//双层循环按照长宽的像素个数迭代每个像素点
    {
        for (var x = 0; x<w; x++)
        {
            key = keyData.charCodeAt(Math.floor(x/DefaultKeyFactor));
            newy = (y + ((h - key)*DefaultKeyFactor))%h;
            pixOff = (w * y  + x )*4;
            newOff = (w * newy + x)*4;
            
            myImageData1.data[newOff] =  imgdata.data[pixOff];
            myImageData1.data[newOff + 1] =  imgdata.data[ pixOff + 1];
            myImageData1.data[newOff + 2] =  imgdata.data[ pixOff + 2];
            myImageData1.data[newOff + 3] =  imgdata.data[ pixOff + 3];
        }
    }


    
    //x trans
    
    for(var y = 0;y< h;y++)//双层循环按照长宽的像素个数迭代每个像素点
    {
        for (var x = 0; x<w; x++)
        {
            key = keyData.charCodeAt(Math.floor(y/DefaultKeyFactor));
            newx = (x + ((w - key)*DefaultKeyFactor)) % w;
            pixOff = (w * y  + x )*4;
            newOff = (w * y + newx)*4;
            
            myImageData2.data[newOff] = myImageData1.data[pixOff];
            myImageData2.data[newOff + 1] = myImageData1.data[pixOff+1];
            myImageData2.data[newOff + 2] = myImageData1.data[pixOff +2];
            myImageData2.data[newOff + 3] = myImageData1.data[pixOff +3];
        }
    }
    
    ctx.putImageData(myImageData2, 0, 0);

}

function test(img, privateKey, ctx){

	var img = new Image();
	img.crossOrigin="anonymous";
	img.src = "http://7xnjb2.com1.z0.glb.clouddn.com/C12B5E66-EC2B-43E0-BBA2-CDD53637B5631445076004";
	var canvas = document.getElementById('canvas');
	var ctx = canvas.getContext('2d');
	img.onload = function() {
        canvas.width= img.naturalWidth;
        canvas.height= img.naturalHeight;
		ctx.drawImage(img, 0, 0);

		var imageData = ctx.getImageData(0, 0, canvas.width, canvas.height); // canvas的长度宽度必须和图像原始的长度宽度一样 
		// max(长度,宽度) = 720
		var key = getKey("123");
		decodeImg(imageData, key, ctx);
	};
	
}





