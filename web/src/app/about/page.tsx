import { Separator } from "@/components/ui/separator";

export default function AboutPage() {
  return (
    <div className="max-w-3xl mx-auto px-4 py-16">
      {/* Hero */}
      <div className="text-center mb-16">
        <p className="text-sm tracking-widest text-[#B8A9C9] mb-4">
          OUR STORY
        </p>
        <h1 className="text-4xl md:text-5xl font-bold text-[#2C3E6B] mb-6">
          달빛처럼, 투명하게.
        </h1>
        <p className="text-lg text-muted-foreground leading-relaxed max-w-xl mx-auto">
          LUNA는 &lsquo;달&rsquo;에서 영감을 받았습니다.
          <br />
          달빛이 밤을 은은하게 비추듯, 우리의 스킨케어도 피부를 자연스럽게 빛나게
          합니다.
        </p>
      </div>

      <Separator className="mb-16" />

      {/* Values */}
      <div className="space-y-12">
        <section>
          <h2 className="text-2xl font-bold mb-4">투명한 성분</h2>
          <p className="text-muted-foreground leading-relaxed">
            모든 성분의 원산지, EWG 등급, 역할을 공개합니다. 무엇이 들어있는지
            숨기지 않습니다. 피부에 닿는 모든 것을 알 권리가 있으니까요.
          </p>
        </section>

        <section>
          <h2 className="text-2xl font-bold mb-4">100% 비건</h2>
          <p className="text-muted-foreground leading-relaxed">
            동물 실험을 하지 않으며, 동물 유래 성분을 사용하지 않습니다. 자연에서
            온 식물 유래 원료만으로 피부에 필요한 것을 채웁니다.
          </p>
        </section>

        <section>
          <h2 className="text-2xl font-bold mb-4">피부 과학</h2>
          <p className="text-muted-foreground leading-relaxed">
            피부에 필요한 것만 넣고, 불필요한 것은 뺍니다. 화려한 마케팅보다
            성분의 효능에 집중합니다. 빼는 것이 더하는 것보다 어렵다는 것을 알기
            때문입니다.
          </p>
        </section>
      </div>

      <Separator className="my-16" />

      {/* Mission */}
      <div className="text-center">
        <blockquote className="text-xl md:text-2xl font-light text-[#2C3E6B] italic leading-relaxed">
          &ldquo;좋은 성분은 숨길 이유가 없습니다.
          <br />
          우리는 모든 것을 투명하게 보여드립니다.&rdquo;
        </blockquote>
        <p className="mt-6 text-sm text-muted-foreground">
          포트폴리오 목적의 가상 브랜드입니다.
        </p>
      </div>
    </div>
  );
}
