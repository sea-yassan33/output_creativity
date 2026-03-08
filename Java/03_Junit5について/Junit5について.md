# Junit5について

## Eclipseの設定

### ①Eclipse に 使用するJDKを読み込ませる

- 以下の手順で実施
```
Window > Preferences
 → Java > Installed JREs
 → Add > Standard VM
 → JDK 17 のパスを指定
```

### ②Mavenプロジェクト作成

- 以下の手順でMavenプロジェクトを作成する
	- File > New > Maven Project
	- maven-archetype-quickstart

![Maven1](https://i.gyazo.com/78f27a8b7c58e6bfb408df68ccaad866.png)

![Maven2](https://i.gyazo.com/9bdc187f3755b85e3160803453a6451a.png)

### ③Project基本設定

- 以下の手順で実施
  - Java Compiler
  	- Enable project specific settings
  	- Compiler compliance level：17
  - Java Build Path
  	- JRE System Library：JavaSE-17

![Project設定](https://i.gyazo.com/456cf588f55e219b98d0d9f9edfcfcb4.png)

![Project設定2](https://i.gyazo.com/fd27aa5b740e6cf420093d83b4bb44d2.png)

### ④pom.xml設定

[pom.xml](./pom.xml)

- 下記を追加
```sh
	<dependencies>
		<!-- JUnit 5 本体 -->
		<dependency>
			<groupId>org.junit.jupiter</groupId>
			<artifactId>junit-jupiter</artifactId>
			<scope>test</scope>
		</dependency>
		<!-- Mockito 5 (inline機能がデフォルトで含まれる) -->
		<dependency>
			<groupId>org.mockito</groupId>
			<artifactId>mockito-core</artifactId>
			<version>5.11.0</version>
			<scope>test</scope>
		</dependency>
		<!-- JUnit 5とMockitoを連携させる拡張 -->
		<dependency>
			<groupId>org.mockito</groupId>
			<artifactId>mockito-junit-jupiter</artifactId>
			<version>5.11.0</version>
			<scope>test</scope>
		</dependency>
	</dependencies>
```

## 主な違いの比較表

|項目 |JUnit 4 (2006年〜)|JUnit 5 (2017年〜)|
|:----|:----|:----|
|Java要求バージョン|Java 5 以上|Java 8 以上|
|アーキテクチャ|単一のJAR（モノリス型）|モジュール構造（必要な機能のみ導入可）|
|パッケージ名|org.junit|org.junit.jupiter.api|
|拡張機能|@RunWith / @Rule|@ExtendWith (拡張性が向上)|
|後方互換性|なし|あり（VintageエンジンでJUnit 4も動く）|

## アノテーションについて

|JUnit 4 (org.junit.*)|JUnit 5 (org.junit.jupiter.api.*)|内容|
|:----|:----|:----|
|Ignore|Disabled|テスト対象外|
|Before|BeforeEach|テスト実行前の処理|
|After|AfterEach|テスト実行後の処理|
|BeforeClass|BeforeAll|テストクラスのテスト実行前に一度だけ行う処理|
|AfterClass|AfterAll|テストクラスのテスト実行後に一度だけ行う処理|

## アサーションについて

|メソッド |説明|
|:----|:----|
|assertEquals(expected, actual)|期待値と実測値が等しいか検証|
|assertNotEquals(unexpected, actual)|値が等しくないことを検証|
|assertTrue(condition)|条件が**true**であるか検証|
|assertFalse(condition)|条件が**false**であるか検証|
|assertNull(actual)|オブジェクトが**null**であるか検証|
|assertNotNull(actual)|オブジェクトが**null**でないか検証|
|assertSame(expected, actual)|同一のオブジェクト（参照が同じ）か検証|
|assertNotSame(unexpected, actual)|異なるオブジェクト（参照が別）か検証|
|assertThrows(Class<T>,Executable)|処理の実行により、指定された例外が送出されることを検証|
|assertTimeout(Duration,Executable)|処理の実行が指定された時間内に終了することを検証|
|fail()|テストを明示的に失敗させる|

## @DisplayNameアノテーション
- テストクラスやテストメソッドに対してわかりやすい名前を付ける事が可能

```java
public class SampleClassTest{
  @Test
  @DisplayName("条件１を通過するかのテスト")
  void test001(){
    // ．．．
  }
  @Test
  @DisplayName("条件2を通過するかのテスト")
  void test002(){
    // ．．．
  }
}
```

## パラメータ化テスト

- 対象コード

```java
public class Sample04 {
	private static String OUR_BANK_CODE = "B001"; // 銀行コード（自分の銀行）

	// 振込手数料の計算を行う
	public int calcFee(String bankCode, int amount) {
		// 振込先が自分の銀行か判定する
		if (OUR_BANK_CODE.equals(bankCode)) {
			// 自分の銀行の場合、30000円以上は無料、それ以外は100円
			if (30000 <= amount) {
				return 0;
			} else {
				return 100;
			}

		} else {
			// 他の銀行の場合、40000円以上は200円、それ以外は500円
			if (40000 <= amount) {
				return 200;
			} else {
				return 500;
			}
		}
	}
}
```

- リテラル配列からパラメータ取得

```java
	@ParameterizedTest(name = "【testNo-{index}】 {arguments}")
	@ValueSource(strings = { "B001,30000,0", "B001,29999,100", "B999,40000,200", "B999,39999,500" })
	@DisplayName("リテラル配列からパラメータ取得")
	void test001(String paramStr) {
		String[] param = paramStr.split(",");
		Sample04 sample04 = new Sample04();

		//
		int result = sample04.calcFee(param[0], Integer.parseInt(param[1]));
		// 検証フェーズ
		assertEquals(Integer.parseInt(param[2]), result);
	}
```

- リストからのパラメータ取得

```java
	@ParameterizedTest(name = "【testNo-{index}】 {arguments}")
	@MethodSource("testData")
	@DisplayName("リストからパラメータ取得")
	void test002(List<String> params) {
		String bankCode = params.get(0);
		int amount = Integer.parseInt(params.get(1));
		int expected = Integer.parseInt(params.get(2));

		Sample04 target = new Sample04();
		int result = target.calcFee(bankCode, amount);

		assertEquals(expected, result);
	}

	static Stream<Arguments> testData() {
		return Stream.of(
				Arguments.of(List.of("B001", "30000", "0")),
				Arguments.of(List.of("B001", "29999", "100")),
				Arguments.of(List.of("B999", "40000", "200")),
				Arguments.of(List.of("B999", "39999", "500")));
	}
```

- リスト（テスト値・戻り値を分離）からパラメータ取得

```java
	@ParameterizedTest(name = "【testNo-{index}】 {arguments}")
	@MethodSource("testData02")
	@DisplayName("リスト（テスト値・戻り値を分離）からパラメータ取得")
	void test003(List<String> input, int expected) {
		String bankCode = input.get(0);
		int amount = Integer.parseInt(input.get(1));

		Sample04 target = new Sample04();
		int result = target.calcFee(bankCode, amount);

		assertEquals(expected, result);
	}

	static Stream<Arguments> testData02() {
		return Stream.of(
				Arguments.of(List.of("B001", "30000"), 0),
				Arguments.of(List.of("B001", "29999"), 100),
				Arguments.of(List.of("B999", "40000"), 200),
				Arguments.of(List.of("B999", "39999"), 500));
	}
```

## PublicメソッドのMock 

- 対象コード

```java
// 【テスト対象】
public class Sample05Display {

	private Sample05Info info = new Sample05Info();

	public String getUserInfoString(String userId) {
		String name = info.getName(userId);
		String gender = info.getGender(userId);
		String old = info.getOld(userId);
		return name + "(" + gender + ") " + old + "歳";
	}
}

public class Sample05Info {
	public String getName(String id) {
		String name = "デフォルト";
		return name;
	}
	public String getGender(String sexId) {
		String gender = "デフォルト";
		return gender;
	}
	public String getOld(String sexId) {
		String old = "デフォルト";
		return old;
	}
}

```

- テストコード

```java
@ExtendWith(MockitoExtension.class) //Mockの際は必須
public class Sample05Test {
	
	@Mock
	private Sample05Info mockInfo;
	private AutoCloseable closeable; //メモリーリーク防止やテストに影響が生じない様に管理
	
	@InjectMocks
	private Sample05Display target;
	
	@BeforeEach
	void setup() {
		closeable = MockitoAnnotations.openMocks(this);
	}
	
	@AfterEach
	void close() throws Exception{
		closeable.close();
	}

	@Test
	@DisplayName("Mockの基本的な使い方")
	void test001() {
		when(mockInfo.getName(anyString())).thenReturn("義堂合六");
		when(mockInfo.getGender(anyString())).thenReturn("女");
		when(mockInfo.getOld(anyString())).thenReturn("22");
		String result = target.getUserInfoString("test");

		assertEquals("義堂合六(女) 22歳", result);
	}
}
```

## voidメソッドのMock

- 対象コード

```java
// 【対象コード】

public class Sample06 {

	public void send(String message) {
		// 本来は外部APIやメール送信など副作用がある処理
		System.out.println("send message: " + message);
	}
}

public class Sample06Service {

	private final Sample06 sample06;

	public Sample06Service(Sample06 sample06) {
		this.sample06 = sample06;
	}

	public void sampleOrder(String orderId) {
		// 何らかの業務処理
		if (orderId == null) {
			throw new IllegalArgumentException("orderId is null");
		}
		// voidメソッド呼び出し
		sample06.send("order placed: " + orderId);

	}
}
```

- テストコード

```java
@ExtendWith(MockitoExtension.class)
public class Sample06Test {
	
	@Mock
	Sample06 sample06;
	
	@InjectMocks
	Sample06Service sample06Service;

	@Test
	@DisplayName("voidメソッドのMockテスト")
	void test001() {
		// voidメソッドは doNothing を使う
		doNothing().when(sample06).send(anyString());

		sample06Service.sampleOrder("A001");

		// 呼ばれたことだけを検証
		verify(sample06).send("order placed: A001");
	}
}
```

## staticメソッドのMock

- 対象コード

```java
public class Sample01 {
	public static void main(String[] args) {
		/**
		 * 複数当選とバリデーション付き
		 */
		List<String> items = List.of("A", "B", "C", "D", "E", "F");
		int n = 3;
		List<String> winners = drawWinners(items, n);
		System.out.println("【当選者】：" + winners);
	}

	public static List<String> drawWinners(List<String> items, int n) {
		// バリデーション
		if (n <= 0) {
			throw new IllegalArgumentException("抽選人数は1人以上にして下さい。");
		}
		if (n > items.size()) {
			throw new IllegalArgumentException("抽選人数は参加者数を超えています。");
		}
		// 逆順した物を返す
		List<String> resultList = reverseListWithStream(items, n);
		return resultList;
	}

	public static List<String> reverseListWithStream(List<String> sampleList, int n) {
		List<String> newList = sampleList.stream().collect(Collectors.toList());
		Collections.reverse(newList);

		return subListMethod(newList, n);
	}

	private static List<String> subListMethod(List<String> sampleList, int n) {
		List<String> tempList = new ArrayList<>(sampleList);
		return tempList.subList(0, n);
	}
}
```

- テストコード

```java
	@Test
	@DisplayName("【staticメソッド】Mockした検証")
	void test05() {
		// テストデータ
		List<String> items = List.of("A", "B", "C");
		int num = 1;

		// ダミーデータ
		List<String> expectedMockResult = List.of("A", "C");

		try (MockedStatic<Sample01> mockedSample01 = mockStatic(Sample01.class, Mockito.CALLS_REAL_METHODS)) {
			mockedSample01.when(() -> Sample01.reverseListWithStream(anyList(), anyInt()))
					.thenReturn(expectedMockResult);

			// 実行
			List<String> actual = Sample01.drawWinners(items, num);

			// 検証
			assertEquals(expectedMockResult, actual);
			// reverseListWithStreamが正しく呼ばれたか検証
			mockedSample01.verify(() -> Sample01.reverseListWithStream(items, num));
		}	
	}
```

## staticメソッドの応答設定

- 応答設定はmockStaticの第2引数などで指定出来ます。

|設定名（org.mockito.Answers） |動作の内容|
|:----|:----|
|RETURNS_DEFAULTS|デフォルト設定。スタブ化していないメソッドは、参照型なら null、基本データ型なら 0 や false を返します。|
|CALLS_REAL_METHODS|スタブ化していないメソッドは、実際の実装（本物のメソッド）を呼び出します。スパイ（Spy）に近い挙動になります。|
|RETURNS_SMART_NULLS|null を返す代わりに、未定義のメソッドが呼ばれたことを示す例外を投げやすい「スマートなNull」を返し、デバッグを容易にします。|
|RETURNS_MOCKS|スタブ化していないメソッドがオブジェクトを返す場合、その返り値を自動的にモック化して返します（連鎖的なモック作成）。|
|RETURNS_DEEP_STUBS|メソッドチェーン（例：A.getB().getC()）のテストを容易にするため、深い階層まで自動的にスタブ化します。|
|RETURNS_SELF|ビルダーパターンなどで自分自身（this）を返すメソッドに対し、自動的にそのモック自身を返します。|

## privateメソッドのテスト方法

- privateメソッドではMockが出来ない為、FieldクラスでPrivateメソッドを可視化してテストを実施します。

```java
	@Test
	@DisplayName("【privateメソッド】 内部で正常に動くか検証")
	void test04() throws Exception {
		// メソッドを取得
		Method method = Sample01.class.getDeclaredMethod("subListMethod", List.class, int.class);
		// privateメソッドへのアクセスを許可
		method.setAccessible(true);
		List<String> input = List.of("X", "Y", "Z");
		// staticメソッドなので第一引数は null
		List<String> result = (List<String>) method.invoke(null, input, 2);
		assertEquals(List.of("X", "Y"), result);
	}
```

## Calender・LocalDateTimeをMockしてテスト

- 対象コード

```java
public class Sample03 {
	
	public static void main(String[] args) {
		List<String> dateList = new ArrayList<>();
		dateList = sampleCalDate();		
		System.out.println(dateList);
	}
	
	private static final List<String> sampleCalDate() {
		List<String> dateList = new ArrayList<>();
		
		// calendarから文字列へ
		Calendar calendar = Calendar.getInstance();
		SimpleDateFormat sdf = new SimpleDateFormat("yyy-MM-dd");
		String calDateStr = sdf.format(calendar.getTime());
		
		// LocalDateから文字列へ
		LocalDateTime now = LocalDateTime.now();
		DateTimeFormatter formatDate = DateTimeFormatter.ofPattern("HH:mm");
		
		// 格納
		dateList.add(calDateStr);
		dateList.add(now.format(formatDate));
		
		return dateList;	
	}
}
```

- テーストコード

```java
@ExtendWith(MockitoExtension.class)
class Sample03Test {

	@Test
	@DisplayName("Calender・LocalDateTimeをMock")
	void test001() throws Exception {
		
		//Mock：Calender
		try(MockedStatic<Calendar> mockCal = mockStatic(Calendar.class,Mockito.CALLS_REAL_METHODS)){
			mockCal.when(Calendar::getInstance).thenAnswer(Invocation ->{
				Calendar newCal = new GregorianCalendar();
				newCal.set(2025, Calendar.JANUARY,2,14,30,00);
				newCal.set(Calendar.MILLISECOND, 0);
				return newCal;
			});
			//Mock：LocalDateTime
			try(MockedStatic<LocalDateTime> mockLocalDate = mockStatic(LocalDateTime.class,Mockito.CALLS_REAL_METHODS)){
				LocalDateTime fakeNow = LocalDateTime.of(2025,1,2,14,30,0);
				mockLocalDate.when(LocalDateTime::now).thenReturn(fakeNow);
				
				Sample03 sample03 = new Sample03();
				
				// privatメソッドを可視化
				Method method = sample03.getClass().getDeclaredMethod("sampleCalDate", null);
				method.setAccessible(true);
				
				List<String> res = (List<String>) method.invoke(sample03, null);
				
				// 検証
				List<String> act = List.of("2025-01-02","14:30");
				assertEquals(res, act);
				
			}	
		}
		
	}
}
```

## 他のパッケージのenumを取り出す方法

```java
package sample.utils;

public class SampleUtils {
	// sample定数
	enum SampleName{
		// 運動
		EXERCISE,
		// 食事
		MEAL,
		// 睡眠
		SLEEP
	}
}
```

- テストコード

```java
package unitreferenc.sample.utils;

import org.junit.jupiter.api.Test;

class SampleUtilsTest extends SampleUtils {

	@Test
	void test() throws Exception {
		Class<?> enumClass = Class.forName("unitreferenc.sample.utils.SampleUtils$SampleName");
		Object exercise = Enum.valueOf((Class<Enum>) enumClass, "EXERCISE");
		
		System.out.println(exercise);
	}

}
```