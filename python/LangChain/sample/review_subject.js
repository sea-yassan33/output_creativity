function getUserData(id) {
  // 1. 変数名が不明瞭
  var data = fetch('https://api.example.com/users/' + id);

  data.then(function(r) {
    return r.json();
  }).then(function(res) {
    // 2. グローバルなスコープを汚染する可能性がある、または古い宣言(var)
    // 3. DOM操作が非効率
    var name = res.user_name;
    document.getElementById('user-name').innerHTML = 'Name: ' + name;
    
    if (res.age > 18) {
      console.log("Adult");
    } else {
      console.log("Minor");
    }
  });
}