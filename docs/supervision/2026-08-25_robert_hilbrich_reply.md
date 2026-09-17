# Email Reply from Robert Hilbrich

**Received by the student:** 2026-08-25

**Source supplied:** Full email body pasted by the student into the project conversation on 2026-08-25

**Exact email sent date and subject:** Not included in the supplied text

**Privacy:** Contains private supervision correspondence; review before any publication or remote push.

The email body below is preserved in German. Email-client whitespace artifacts were normalized; the wording was not substantively edited.

---

Liebe Yuhong Zhang,

sehr gerne – ich werde versuchen, Sie möglichst gut bei Ihrer Masterarbeit zu unterstützen. Es freut uns, dass Sie dafür SUMO verwenden wollen.

Zum Framework würde ich zunächst bei sumoITScontrol bleiben. Wir haben das Framework auf der SUMO Conference 2026 gesehen und wollten es uns ohnehin einmal genauer anschauen. Mir ist derzeit kein vergleichbares Gesamtframework im SUMO-Umfeld bekannt, das verschiedene etablierte Regelverfahren zusammen mit einer systematischen Auswertung über mehrere Seeds bereitstellt. Für die Arbeit erscheint mir das daher als eine sinnvolle Grundlage. Mit ALINEA anzufangen, halte ich ebenfalls für richtig; damit hätten Sie zunächst einen etablierten und vergleichsweise überschaubaren Regler als Ausgangspunkt.

Auch das vorgeschlagene synthetische Szenario finde ich grundsätzlich sinnvoll. Ich würde es für den Anfang bewusst einfach halten: eine Autobahn mit einer Auffahrt und ein kleines vorgelagertes Stadtnetz mit einer zunächst festzeitgesteuerten LSA. Die Rasterung der Verkehrsnachfrage ohne Regelung ist aus meiner Sicht ein guter erster Schritt, um das Verhalten des Szenarios und insbesondere den Bereich um den Verkehrszusammenbruch zunächst kennenzulernen.

Als bewusst vereinfachte Ausgangshypothese könnten wir zunächst annehmen, dass der Zufluss von der Rampe die verbleibende Kapazität der Hauptfahrbahn, also C−qMain, nicht überschreiten sollte.

Interessant wird es aber aus mehreren Gründen:

- Die tatsächliche Kapazität ist nicht konstant und zudem nicht direkt bekannt.
- Der Merge selbst beeinflusst die effektiv verfügbare Kapazität; der Zusammenhang zwischen qMain, qRamp und der Gesamtkapazität ist daher nicht rein statisch.
- Nach einem Breakdown kann die Abflusskapazität aufgrund des Capacity Drops geringer sein als zuvor.
- Die Nachfrage auf der Rampe kann größer sein als die zulässige Zuflussrate. Dann wächst zwangsläufig die Warteschlange.
- Die Rampe hat nur einen begrenzten Stauraum. Wenn ein Rückstau in das untergeordnete Netz vermieden werden soll, muss irgendwann mehr Verkehr freigegeben werden, obwohl die Autobahn eigentlich keine entsprechende Restkapazität mehr hat.

Gerade der letzte Punkt ist meines Erachtens ein interessanter Kern der Arbeit: Wann sollte die Rampenregelung zugunsten des untergeordneten Netzes zurückgenommen bzw. übersteuert werden?

Beim Fahrzeugfolgemodell würde ich zunächst mit dem SUMO-Standardmodell Krauß und den Default-Parametern beginnen. Ohne empirische Daten für eine Kalibrierung würde ich an dieser Stelle nicht versuchen, durch eine spezielle Parametrisierung ein bestimmtes Verhalten zu erzwingen. Stattdessen würde ich zunächst untersuchen, ob sich mit dem gewählten Szenario ein plausibler Verkehrszusammenbruch und Capacity-Drop ergibt. Falls nicht, sollten wir uns gezielt anschauen, woran das liegt – dabei können neben dem Fahrzeugfolgemodell beispielsweise auch das Spurwechsel- und Einfädelverhalten, die Geometrie der Auffahrt und die Nachfrage eine Rolle spielen.

Wichtig ist bei solchen Kapazitätsuntersuchungen außerdem, die Fahrzeugeinspeisung in SUMO passend zu konfigurieren. Mit den Standardwerten für departPos, departLane und departSpeed kann die Einsetzung selbst den erreichbaren Zufluss begrenzen. Für hohe Verkehrsstärken sollten wir daher z. B. mit departPos="last", departLane="best" und departSpeed="max" arbeiten bzw. generell prüfen, dass die gewünschte Nachfrage tatsächlich in das Netz eingespeist werden kann.

Den zeitlichen Ablauf kann ich so bestätigen. So wie ich den Prozess verstanden habe, gibt es zunächst eine Zwischenpräsentation bei Herrn Prof. Nagel. Zu diesem Zeitpunkt sollte die Fragestellung bereits hinreichend konkretisiert sein und es sollten auch Vorschläge für den Titel der Arbeit vorliegen. Im Anschluss kann das Thema noch einmal gemeinsam nachgeschärft werden; danach erfolgt die offizielle Anmeldung und damit beginnt die viermonatige Bearbeitungszeit.

Ihr vorgeschlagener Zeitplan erscheint mir daher realistisch. Eine Zwischenpräsentation Ende Oktober bzw. Anfang November und die anschließende Anmeldung würden auf eine Abgabe im Februar oder März hinauslaufen. Bis zur Zwischenpräsentation wäre es aus meiner Sicht sinnvoll, das Framework zum Laufen zu bringen, das Szenario aufzubauen und erste Ergebnisse für den ungeregelten Fall zu haben. Dann hätten wir eine gute Grundlage, um Fragestellung und Umfang der Arbeit vor der Anmeldung noch einmal zu prüfen.

Für mich wäre es grundsätzlich kein Problem, wenn Sie die Arbeit auf Englisch schreiben. Ob es allerdings seitens des Lehrstuhls bzw. der Prüfungsmodalitäten hierzu noch besondere Vorgaben gibt, sollten Sie sicherheitshalber noch einmal dort klären.

Mit besten Grüßen

Robert Hilbrich
