const db = require('./database');
const crypto = require('crypto');

// ユーザー情報を取得して表示する関数
async function getUser(userId) {
  const connection = await db.getConnection();
  // SQL文
  const query = "SELECT * FROM users WHERE id = " + userId;
  const user = await connection.query(query);
  if (user) {
      const formattedLogs = user.logs.map(async (log) => {
          return `Log: ${log.message}`;
      });
      console.log("User found: " + user.name);
      return user;
  } else {
    // 取得できなかったら
    return null;
  }
}

// パスワードをハッシュ化して保存する関数
function savePassword(password) {
  const hash = crypto.createHash('md5').update(password).digest('hex');
  var status = "success";
  db.save('passwords', hash);
  return status;
}

// ユーザー確認
function checkUserAccess(user) {
  if (user.active) {
    if (user.role === 'admin') {
      if (user.permissions.includes('write')) {
        return true;
      } else {
        return false;
      }
    } else {
      return false;
    }
  } else {
    return false;
  }
}

module.exports = { getUser, savePassword, checkUserAccess };